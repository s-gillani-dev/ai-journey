/* tslint:disable */
/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import {GoogleGenAI, LiveServerMessage, Modality, Session} from '@google/genai';
import {LitElement, css, html} from 'lit';
import {customElement, query, state} from 'lit/decorators.js';
import {createBlob, decode} from './utils';
import './talking-head';
import type {GdmTalkingHead} from './talking-head';

@customElement('gdm-live-audio')
export class GdmLiveAudio extends LitElement {
  @state() isRecording = false;
  @state() isConnecting = false;
  @state() status = '';
  @state() error = '';
  @state() inputTranscript = '';
  @state() outputTranscript = '';

  @query('gdm-talking-head') private talkingHead!: GdmTalkingHead;

  private client: GoogleGenAI;
  private session: Session | null = null;
  private sessionId = 0;        // incremented each time we open a session
  private sessionOpen = false;
  private sending = false;
  private inputAudioContext = new AudioContext({sampleRate: 16000});
  private mediaStream: MediaStream;
  private sourceNode: MediaStreamAudioSourceNode;
  private workletNode: AudioWorkletNode | null = null;
  private workletReady = false;

  static styles = css`
    :host {
      display: block;
      width: 100vw;
      height: 100vh;
      overflow: hidden;
    }

    #app-layout {
      position: relative;
      width: 100%;
      height: 100%;
    }

    gdm-talking-head {
      display: block;
      width: 100%;
      height: 100%;
    }

    #status {
      position: absolute;
      bottom: 5vh;
      left: 0;
      right: 0;
      z-index: 10;
      text-align: center;
      color: rgba(255,255,255,0.7);
      font-family: sans-serif;
      font-size: 13px;
    }

    .controls {
      z-index: 10;
      position: absolute;
      bottom: 10vh;
      left: 0;
      right: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      gap: 10px;

      button {
        outline: none;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.1);
        width: 64px;
        height: 64px;
        cursor: pointer;
        font-size: 24px;
        padding: 0;
        margin: 0;

        &:hover {
          background: rgba(255, 255, 255, 0.2);
        }
      }

      button[disabled] {
        display: none;
      }
    }

    #transcripts {
      position: absolute;
      bottom: 22vh;
      left: 4vw;
      right: 4vw;
      z-index: 10;
      display: flex;
      flex-direction: column;
      gap: 8px;
      pointer-events: none;
    }

    .tx-user {
      align-self: flex-end;
      background: rgba(59, 130, 246, 0.75);
      color: #fff;
      font-family: sans-serif;
      font-size: 14px;
      line-height: 1.4;
      padding: 6px 14px;
      border-radius: 16px 16px 4px 16px;
      max-width: 70%;
      text-align: right;
      backdrop-filter: blur(4px);
    }

    .tx-ai {
      align-self: flex-start;
      background: rgba(20, 20, 20, 0.75);
      color: rgba(255,255,255,0.93);
      font-family: sans-serif;
      font-size: 14px;
      line-height: 1.4;
      padding: 6px 14px;
      border-radius: 16px 16px 16px 4px;
      max-width: 70%;
      backdrop-filter: blur(4px);
    }
  `;

  constructor() {
    super();
    // Patch WebSocket.prototype.send once so the SDK can never throw on a
    // closing/closed socket — it just silently drops the send instead.
    if (!(WebSocket.prototype.send as any).__patched) {
      const orig = WebSocket.prototype.send;
      WebSocket.prototype.send = function(this: WebSocket, data: any) {
        if (this.readyState === WebSocket.OPEN) orig.call(this, data);
      };
      (WebSocket.prototype.send as any).__patched = true;
    }

    // Only create the client — session opens lazily on first startRecording()
    this.client = new GoogleGenAI({
      apiKey: process.env.GEMINI_API_KEY,
    });
  }

  /** Opens a new Gemini Live session. Resolves (with session assigned) when the WebSocket is open. */
  private async connectSession(): Promise<void> {
    const model = 'gemini-2.5-flash-native-audio-preview-09-2025';

    // Give any in-flight WebSocket close a full tick to finish before opening a new one
    await new Promise(r => setTimeout(r, 0));

    // Stamp this attempt so stale callbacks from a previous session are ignored
    const myId = ++this.sessionId;

    const session = await this.client.live.connect({
      model,
      callbacks: {
        onopen: () => {
          if (this.sessionId !== myId) return;
          this.sessionOpen = true;
          this.updateStatus('Connected');
        },
        onmessage: async (message: LiveServerMessage) => {
          if (this.sessionId !== myId) return;

          // Output transcript — display it and feed to avatar for lipsync.
          // addTranscript is called BEFORE speakPCM so the transcript words
          // are pending when the audio chunk is processed on the same message.
          const outTx = (message.serverContent as any)?.outputTranscription?.text;
          if (outTx) {
            this.outputTranscript += outTx;
            this.talkingHead?.addTranscript(outTx);
          }

          // Each audio chunk is immediately streamed to the avatar.
          // First audio plays within ms of the first chunk arriving.
          const parts = message.serverContent?.modelTurn?.parts ?? [];
          for (const part of parts) {
            if (part.inlineData?.data) {
              this.talkingHead?.speakPCM(decode(part.inlineData.data));
            }
          }

          // Input transcript — show what the user said
          const inTx = (message.serverContent as any)?.inputTranscription?.text;
          if (inTx) this.inputTranscript = inTx;

          if (message.serverContent?.turnComplete) {
            this.talkingHead?.flushPCM();
          }

          if (message.serverContent?.interrupted) {
            this.outputTranscript = '';
            this.talkingHead?.interrupt();
          }
        },
        onerror: (e: ErrorEvent) => {
          if (this.sessionId !== myId) return;
          this.sessionOpen = false;
          this.updateError(e.message);
        },
        onclose: (e: CloseEvent) => {
          if (this.sessionId !== myId) return;
          this.sessionOpen = false;
          this.session = null;
          if (this.isRecording) {
            this.teardownMic();
          }
          const reason = e.reason || `code ${e.code}`;
          this.updateError(`Disconnected: ${reason}`);
        },
      },
      config: {
        systemInstruction: {
          parts: [{ text: 'You are a helpful voice assistant. Always respond in English only. Transcribe user speech in English only.' }],
        },
        responseModalities: [Modality.AUDIO],
        inputAudioTranscription: {},
        outputAudioTranscription: {},
        speechConfig: {
          voiceConfig: {prebuiltVoiceConfig: {voiceName: 'Orus'}},
        },
      },
    });

    // Only store if this attempt is still the current one
    if (this.sessionId === myId) {
      this.session = session;
    } else {
      // Superseded — close the just-opened session immediately
      try { session.close(); } catch { /* ignore */ }
    }
  }

  private updateStatus(msg: string) {
    this.status = msg;
  }

  private updateError(msg: string) {
    this.error = msg;
  }

  private async startRecording() {
    if (this.isRecording || this.isConnecting) return;
    this.isConnecting = true;
    this.error = '';
    this.inputTranscript = '';
    this.outputTranscript = '';

    try {
      // 1. Acquire mic BEFORE opening the session so audio is ready to flow
      //    the instant the WebSocket opens — prevents server-side idle timeouts.
      this.updateStatus('Requesting microphone access…');
      await this.inputAudioContext.resume();
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: false,
      });

      this.sourceNode = this.inputAudioContext.createMediaStreamSource(this.mediaStream);

      if (!this.workletReady) {
        await this.inputAudioContext.audioWorklet.addModule('/pcm-processor.js');
        this.workletReady = true;
      }

      this.workletNode = new AudioWorkletNode(this.inputAudioContext, 'pcm-processor');
      this.workletNode.port.onmessage = (e: MessageEvent<Float32Array>) => {
        if (!this.isRecording || !this.session || !this.sessionOpen || !this.sending) return;
        try {
          this.session.sendRealtimeInput({media: createBlob(e.data)});
        } catch {
          // Session may have closed — ignore
        }
      };

      this.sourceNode.connect(this.workletNode);
      this.workletNode.connect(this.inputAudioContext.destination);

      // 2. Close any stale session
      if (this.session) {
        this.sessionOpen = false;
        try { this.session.close(); } catch { /* ignore */ }
        this.session = null;
      }

      // 3. Open session — audio pipeline already running so data flows immediately
      this.updateStatus('Connecting…');
      await this.connectSession();

      // 4. Guard: if the session closed before connect() resolved, bail cleanly
      if (!this.session || !this.sessionOpen) {
        this.teardownMic();
        this.updateError('Session closed immediately — check API key or model name.');
        return;
      }

      // 5. Everything ready — go live
      this.sending = true;
      this.isRecording = true;
      this.updateStatus('🔴 Recording...');
    } catch (err: unknown) {
      console.error('Error starting recording:', err);
      this.updateError(`Error: ${(err as Error).message ?? String(err)}`);
      this.teardownMic();
      if (this.session) {
        this.sessionOpen = false;
        try { this.session.close(); } catch { /* ignore */ }
        this.session = null;
      }
    } finally {
      this.isConnecting = false;
    }
  }

  /** Tears down only the audio pipeline — never touches the session. */
  private teardownMic() {
    this.sending = false;  // block worklet immediately — must be first
    this.isRecording = false;

    if (this.workletNode) {
      this.workletNode.port.onmessage = null;
      this.workletNode.disconnect();
      this.workletNode = null;
    }
    if (this.sourceNode) {
      this.sourceNode.disconnect();
      (this as any).sourceNode = null;
    }
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop());
      (this as any).mediaStream = null;
    }
  }

  private stopRecording() {
    if (!this.isRecording && !this.mediaStream) return;

    this.updateStatus('Stopping recording...');
    this.sending = false;
    this.teardownMic();

    if (this.session) {
      this.sessionOpen = false;
      try { this.session.close(); } catch { /* ignore */ }
      this.session = null;
    }

    this.updateStatus('Recording stopped. Click Start to begin again.');
  }

  private reset() {
    this.inputTranscript = '';
    this.outputTranscript = '';
    this.sessionOpen = false;
    if (this.session) {
      try { this.session.close(); } catch { /* ignore */ }
      this.session = null;
    }
    this.teardownMic();
    this.updateStatus('Session cleared.');
  }

  render() {
    return html`
      <div id="app-layout">
        <gdm-talking-head></gdm-talking-head>

        <!-- Controls overlay -->
        <div class="controls">
          <button
            id="resetButton"
            @click=${this.reset}
            ?disabled=${this.isRecording || this.isConnecting}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              height="40px"
              viewBox="0 -960 960 960"
              width="40px"
              fill="#ffffff">
              <path
                d="M480-160q-134 0-227-93t-93-227q0-134 93-227t227-93q69 0 132 28.5T720-690v-110h80v280H520v-80h168q-32-56-87.5-88T480-720q-100 0-170 70t-70 170q0 100 70 170t170 70q77 0 139-44t87-116h84q-28 106-114 173t-196 67Z" />
            </svg>
          </button>
          <button
            id="startButton"
            @click=${this.startRecording}
            ?disabled=${this.isRecording || this.isConnecting}>
            <svg
              viewBox="0 0 100 100"
              width="32px"
              height="32px"
              fill="#c80000"
              xmlns="http://www.w3.org/2000/svg">
              <circle cx="50" cy="50" r="50" />
            </svg>
          </button>
          <button
            id="stopButton"
            @click=${this.stopRecording}
            ?disabled=${!this.isRecording}>
            <svg
              viewBox="0 0 100 100"
              width="32px"
              height="32px"
              fill="#000000"
              xmlns="http://www.w3.org/2000/svg">
              <rect x="0" y="0" width="100" height="100" rx="15" />
            </svg>
          </button>
        </div>

        <!-- Transcripts -->
        <div id="transcripts">
          ${this.inputTranscript ? html`<div class="tx-user">${this.inputTranscript}</div>` : ''}
          ${this.outputTranscript ? html`<div class="tx-ai">${this.outputTranscript}</div>` : ''}
        </div>

        <div id="status">${this.error || this.status}</div>
      </div>
    `;
  }
}
