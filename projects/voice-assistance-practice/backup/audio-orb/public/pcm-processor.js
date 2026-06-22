/**
 * AudioWorklet processor — captures mono float32 mic input and forwards each
 * quantum (128 samples) to the main thread as a copy of the Float32Array.
 */
class PCMProcessor extends AudioWorkletProcessor {
  process(inputs) {
    const channel = inputs[0]?.[0];
    if (channel) {
      // slice() copies the buffer — the underlying allocation is reused each quantum
      this.port.postMessage(channel.slice());
    }
    return true; // keep processor alive
  }
}

registerProcessor('pcm-processor', PCMProcessor);
