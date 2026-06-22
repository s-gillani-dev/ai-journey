/**
 * GdmTalkingHead — Lit wrapper around the TalkingHead 3-D avatar library.
 *
 * Public API:
 *   el.speakPCM(uint8Array)  — feed raw 16-bit PCM (24 kHz, mono) from Gemini
 *   el.addTranscript(text)   — accumulate transcript text for lipsync
 *   el.flushPCM()            — signal end of turn (turnComplete)
 *   el.interrupt()           — stop current speech immediately
 */

import { LitElement, html, css } from 'lit';
import { customElement, state, query } from 'lit/decorators.js';

const AVATAR_URL =
  '/avatars/brunette.glb?morphTargets=ARKit,Oculus+Visemes,mouthOpen,mouthSmile,eyesClosed,eyesLookUp,eyesLookDown';

const SAMPLE_RATE = 24000; // Gemini Live PCM output rate

@customElement('gdm-talking-head')
export class GdmTalkingHead extends LitElement {
  // -------------------------------------------------------------------------
  // Private state
  // -------------------------------------------------------------------------
  private headInstance: any = null;
  private audioCtx: AudioContext | null = null;

  // Per-turn audio streaming state
  private newStreamTurn = true;
  private scheduledUntil = 0; // Web Audio time up to which audio is scheduled
  private pendingWordText = '';
  private streamAccumMs = 0;  // ms of audio sent this turn (for word offset tracking)

  @state() private scriptsLoaded = false;
  @state() private activated = false;
  @state() private isLoading = false;
  @state() private isSpeaking = false;
  @state() private statusText = '';

  @query('#th-container') private container!: HTMLDivElement;

  // -------------------------------------------------------------------------
  // Styles
  // -------------------------------------------------------------------------
  static styles = css`
    :host {
      display: block;
      position: relative;
      width: 100%;
      height: 100%;
      background: #1a1a2e;
      border-radius: 12px;
      overflow: hidden;
    }

    #th-container {
      width: 100%;
      height: 100%;
    }

    /* ---- overlays ---- */
    .overlay {
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(16, 12, 20, 0.92);
      cursor: pointer;
      z-index: 10;
      transition: background 0.2s;
    }
    .overlay:hover {
      background: rgba(16, 12, 20, 0.8);
    }
    .overlay-inner {
      text-align: center;
      color: #fff;
      font-family: sans-serif;
      user-select: none;
    }
    .spinner {
      width: 48px;
      height: 48px;
      border: 3px solid rgba(255, 255, 255, 0.2);
      border-top-color: #fff;
      border-radius: 50%;
      margin: 0 auto 16px;
      animation: spin 0.9s linear infinite;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    .play-btn {
      width: 72px;
      height: 72px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.15);
      border: 2px solid rgba(255, 255, 255, 0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 16px;
      transition: background 0.2s;
    }
    .overlay:hover .play-btn {
      background: rgba(255, 255, 255, 0.25);
    }
    .overlay h2 {
      margin: 0 0 6px;
      font-size: 18px;
      font-weight: 600;
    }
    .overlay p {
      margin: 0;
      font-size: 13px;
      color: rgba(255, 255, 255, 0.6);
    }

    /* ---- status badge ---- */
    .badge {
      position: absolute;
      top: 10px;
      left: 10px;
      padding: 4px 10px;
      border-radius: 6px;
      font-family: sans-serif;
      font-size: 12px;
      font-weight: 600;
      color: #fff;
      z-index: 5;
      pointer-events: none;
    }
    .badge-speaking {
      background: rgba(200, 0, 0, 0.75);
    }
    .badge-loading {
      background: rgba(0, 0, 0, 0.6);
    }
  `;

  // -------------------------------------------------------------------------
  // Lifecycle
  // -------------------------------------------------------------------------
  connectedCallback() {
    super.connectedCallback();
    if ((window as any).TalkingHead) {
      this.scriptsLoaded = true;
    } else {
      window.addEventListener('talkinghead-loaded', this._onLibLoaded);
      window.addEventListener('talkinghead-error', this._onLibError);
    }
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    window.removeEventListener('talkinghead-loaded', this._onLibLoaded);
    window.removeEventListener('talkinghead-error', this._onLibError);
    try { this.headInstance?.stop?.(); } catch { /* ignore */ }
  }

  private _onLibLoaded = () => { this.scriptsLoaded = true; };
  private _onLibError  = () => { this.statusText = 'Failed to load TalkingHead'; };

  // -------------------------------------------------------------------------
  // Activation (requires user gesture for AudioContext)
  // -------------------------------------------------------------------------
  private async _handleActivate() {
    if (!this.scriptsLoaded) return;
    this.activated = true;
    await this._initAvatar();
  }

  private async _initAvatar() {
    const TH = (window as any).TalkingHead;
    if (!TH) { this.statusText = 'TalkingHead not available'; return; }

    try {
      this.isLoading = true;
      this.statusText = 'Loading avatar…';

      await this.updateComplete;

      // Create a 24 kHz AudioContext and pass it to TalkingHead.
      // TalkingHead will use this context for all its audio nodes, including
      // audioStreamGainNode which we tap into for gapless BufferSourceNode playback.
      this.audioCtx = new AudioContext({ sampleRate: SAMPLE_RATE });
      await this.audioCtx.resume();

      this.headInstance = new TH(this.container, {
        ttsEndpoint: 'https://texttospeech.googleapis.com/v1/text:synthesize',
        jwtGet: () => Promise.resolve('local-no-tts'),
        lipsyncModules: ['en'],
        lipsyncLang: 'en',
        modelFPS: 30,
        cameraView: 'full',
        avatarMute: false,
        pcmSampleRate: SAMPLE_RATE,
        audioCtx: this.audioCtx,
      });

      await this.headInstance.showAvatar({
        url: AVATAR_URL,
        body: 'F',
        avatarMood: 'neutral',
        lipsyncLang: 'en',
      });

      // Sync to whatever AudioContext TalkingHead actually ended up using.
      // TH may rebuild its audio graph during showAvatar/init, making its
      // this.audioCtx a different object than the one we passed in.
      // audioStreamGainNode belongs to this.headInstance.audioCtx, so our
      // BufferSourceNodes must be created from the same context.
      this.audioCtx = this.headInstance.audioCtx ?? this.audioCtx;
      await this.audioCtx!.resume();

      this.isLoading = false;
      this.statusText = 'Ready';
    } catch (err: any) {
      this.isLoading = false;
      this.statusText = `Avatar error: ${err?.message ?? err}`;
      console.error('[TalkingHead] Avatar init error:', err);
    }
  }

  // -------------------------------------------------------------------------
  // Public API
  // -------------------------------------------------------------------------

  /**
   * Feed a raw 16-bit PCM chunk (24 kHz, mono) from Gemini Live.
   *
   * Audio is played immediately via a Web Audio BufferSourceNode at
   * SAMPLE_RATE (24 kHz) so the browser resamples to hardware rate
   * automatically — avoiding the 2 × speed bug that the streaming worklet
   * has on macOS when audioCtx.sampleRate ≠ hardware rate.
   *
   * Lipsync visemes are injected directly into TalkingHead's animQueue with
   * future absolute animClock timestamps so they fire in sync with the audio.
   */
  speakPCM(data: Uint8Array) {
    if (!this.headInstance || !this.audioCtx) return;
    const ctx = this.audioCtx;
    if (ctx.state === 'suspended') ctx.resume().catch(() => {});

    if (this.newStreamTurn) {
      this.newStreamTurn = false;
      this.streamAccumMs = 0;
      // Start audio 50 ms from now so we have a non-negative future time even
      // if the very first chunk arrives before resume() fully completes.
      this.scheduledUntil = ctx.currentTime + 0.05;
      // Trigger natural speaking body animation (gestures, head movement).
      try { this.headInstance.speakWithHands?.(); } catch { /* ignore */ }
    }

    // Int16 → Float32 → AudioBuffer stamped at SAMPLE_RATE.
    // Web Audio's AudioBufferSourceNode handles resampling to hardware rate
    // automatically, keeping correct pitch/speed regardless of ctx.sampleRate.
    const int16 = new Int16Array(data.buffer, data.byteOffset, Math.floor(data.byteLength / 2));
    const float32 = new Float32Array(int16.length);
    for (let i = 0; i < int16.length; i++) float32[i] = int16[i] / 32768;
    const buf = ctx.createBuffer(1, float32.length, SAMPLE_RATE);
    buf.copyToChannel(float32, 0);

    const chunkMs = (int16.length / SAMPLE_RATE) * 1000;
    // ms from NOW until this chunk's audio starts playing.
    const msUntilChunk = (this.scheduledUntil - ctx.currentTime) * 1000;

    // Route audio through TH's stream gain → reverb → destination.
    // This is the same node the TH streaming worklet uses, keeping volume
    // control and head-bobbing analysis intact.
    const source = ctx.createBufferSource();
    source.buffer = buf;
    source.connect(this.headInstance.audioStreamGainNode);
    source.start(this.scheduledUntil);
    this.scheduledUntil += buf.duration;

    // Inject per-phoneme visemes into animQueue at future absolute animClock
    // timestamps aligned to when the audio for each word will actually play.
    if (this.pendingWordText.trim()) {
      const words = this.pendingWordText.trim().split(/\s+/).filter(Boolean);
      if (words.length > 0) {
        const perWord = chunkMs / words.length;
        const animNow = this.headInstance.animClock as number;
        for (let wi = 0; wi < words.length; wi++) {
          const wordStartMs = animNow + msUntilChunk + wi * perWord;
          const wrd = this.headInstance.lipsyncPreProcessText(words[wi], 'en');
          const val = this.headInstance.lipsyncWordsToVisemes(wrd, 'en');
          if (val?.visemes?.length) {
            const dTotal = val.times[val.visemes.length - 1]
              + val.durations[val.visemes.length - 1];
            const cap = Math.min(perWord, val.visemes.length * 200);
            for (let j = 0; j < val.visemes.length; j++) {
              const t = wordStartMs + (dTotal > 0 ? (val.times[j] / dTotal) * cap : 0);
              const d = dTotal > 0
                ? (val.durations[j] / dTotal) * cap
                : cap / val.visemes.length;
              const level = (val.visemes[j] === 'PP' || val.visemes[j] === 'FF') ? 0.9 : 0.6;
              // Push directly to animQueue with absolute animClock timestamps.
              // The ts array is [fade-in-start, peak, fade-out-end].
              // Values array: [null = current morph value, peak, 0 = silent].
              this.headInstance.animQueue.push({
                template: { name: 'viseme' },
                ts: [
                  t - Math.min(60, (2 * d) / 3),
                  t + Math.min(25, d / 2),
                  t + d + Math.min(60, d / 2),
                ],
                vs: { ['viseme_' + val.visemes[j]]: [null, level, 0] },
              });
            }
          }
        }
      }
      this.pendingWordText = '';
    }

    this.streamAccumMs += chunkMs;
    this.isSpeaking = true;
  }

  /** Accumulate transcript text. Call BEFORE speakPCM for the same message. */
  addTranscript(text: string) {
    this.pendingWordText += text;
  }

  /**
   * Signal end of turn (turnComplete).
   * Resets per-turn state so the next speakPCM call starts a fresh stream.
   */
  flushPCM() {
    this.newStreamTurn = true;
    this.pendingWordText = '';
    // Clear isSpeaking after the last scheduled audio drains.
    if (this.audioCtx && this.scheduledUntil > this.audioCtx.currentTime) {
      const remaining = (this.scheduledUntil - this.audioCtx.currentTime) * 1000;
      setTimeout(() => { this.isSpeaking = false; }, remaining + 200);
    } else {
      this.isSpeaking = false;
    }
  }

  /** Stop speech immediately and reset for the next turn. */
  interrupt() {
    this.newStreamTurn = true;
    this.pendingWordText = '';
    this.isSpeaking = false;
    // Kill in-flight audio by ramping the stream gain to 0 then restoring.
    if (this.headInstance?.audioStreamGainNode && this.audioCtx) {
      const gain = this.headInstance.audioStreamGainNode.gain;
      gain.cancelScheduledValues(this.audioCtx.currentTime);
      gain.setValueAtTime(0, this.audioCtx.currentTime);
      gain.setValueAtTime(1, this.audioCtx.currentTime + 0.1);
    }
    // Remove pending visemes injected for the interrupted turn.
    if (this.headInstance?.animQueue) {
      this.headInstance.animQueue = (this.headInstance.animQueue as any[]).filter(
        (x: any) => x.template?.name !== 'viseme'
      );
    }
  }

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------
  render() {
    return html`
      <div id="th-container"></div>

      <!-- Pre-activation overlay -->
      ${!this.activated ? html`
        <div class="overlay" @click=${this._handleActivate}>
          <div class="overlay-inner">
            ${!this.scriptsLoaded ? html`
              <div class="spinner"></div>
              <p>Loading TalkingHead…</p>
            ` : html`
              <div class="play-btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="white">
                  <path d="M8 5v14l11-7z"/>
                </svg>
              </div>
              <h2>Click to activate avatar</h2>
              <p>Required by browser audio policy</p>
            `}
          </div>
        </div>
      ` : ''}

      <!-- Loading overlay (after activation) -->
      ${this.activated && this.isLoading ? html`
        <div class="overlay" style="cursor:default">
          <div class="overlay-inner">
            <div class="spinner"></div>
            <p>${this.statusText}</p>
          </div>
        </div>
      ` : ''}

      <!-- Speaking badge -->
      ${this.isSpeaking ? html`
        <div class="badge badge-speaking">Speaking…</div>
      ` : ''}
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'gdm-talking-head': GdmTalkingHead;
  }
}
