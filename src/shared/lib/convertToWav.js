export const convertToWav = async (blob) => {
    const arrayBuffer = await blob.arrayBuffer();
    const audioCtx = new AudioContext();
    const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);
    await audioCtx.close();

    const numChannels = audioBuffer.numberOfChannels;
    const sampleRate = audioBuffer.sampleRate;
    const numSamples = audioBuffer.length;
    const byteLength = 44 + numSamples * numChannels * 2;

    const buffer = new ArrayBuffer(byteLength);
    const view = new DataView(buffer);

    const write = (offset, str) => {
        for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i));
    };

    write(0, 'RIFF');
    view.setUint32(4, byteLength - 8, true);
    write(8, 'WAVE');
    write(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * numChannels * 2, true);
    view.setUint16(32, numChannels * 2, true);
    view.setUint16(34, 16, true);
    write(36, 'data');
    view.setUint32(40, numSamples * numChannels * 2, true);

    let offset = 44;
    for (let i = 0; i < numSamples; i++) {
        for (let ch = 0; ch < numChannels; ch++) {
            const s = Math.max(-1, Math.min(1, audioBuffer.getChannelData(ch)[i]));
            view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
            offset += 2;
        }
    }

    return new Blob([buffer], { type: 'audio/wav' });
};
