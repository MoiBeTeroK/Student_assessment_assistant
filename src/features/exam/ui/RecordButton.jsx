import { useState, useEffect, useRef } from 'react';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import {
    PlayArrow as PlayIcon,
    Stop as StopIcon,
    Pause as PauseIcon,
    Replay as ReplayIcon,
} from '@mui/icons-material';

const BAR_COUNT = 40;

const analyzeBlob = async (blob) => {
    try {
        const arrayBuffer = await blob.arrayBuffer();
        const audioCtx = new AudioContext();
        const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);
        const data = audioBuffer.getChannelData(0);
        const step = Math.floor(data.length / BAR_COUNT);

        const rawValues = Array.from({ length: BAR_COUNT }, (_, i) => {
            const slice = data.slice(i * step, (i + 1) * step);
            const rms = Math.sqrt(slice.reduce((s, v) => s + v * v, 0) / slice.length);
            return rms;
        });

        const max = Math.max(...rawValues, 0.001);
        const normalized = rawValues.map((v) => v / max);

        return normalized.map((v) => Math.pow(v, 0.4));
    } catch {
        return Array.from({ length: BAR_COUNT }, (_, i) =>
            0.1 + 0.9 * Math.abs(Math.sin(i * 0.4) * Math.cos(i * 0.15))
        );
    }
};

const Waveform = ({ bars, progress }) => (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: '2px', height: 36 }}>
        {bars.map((h, i) => {
            const played = i / BAR_COUNT < progress;
            return (
                <Box
                    key={i}
                    sx={{
                        width: 3,
                        borderRadius: 2,
                        height: `${Math.max(3, h * 34)}px`,
                        backgroundColor: played ? '#F9F5ED' : 'rgba(249,245,237,0.35)',
                        transition: 'background-color 0.1s ease',
                        flexShrink: 0,
                    }}
                />
            );
        })}
    </Box>
);

export const RecordButton = ({ questionId, isRecording, isDone, blob, onStart, onStop, onRerecord }) => {
    const [bars, setBars] = useState([]);
    const [isPlaying, setIsPlaying] = useState(false);
    const [playProgress, setPlayProgress] = useState(0);
    const audioRef = useRef(null);
    const progressTimer = useRef(null);

    useEffect(() => {
        if (blob) {
            analyzeBlob(blob).then(setBars);
            setIsPlaying(false);
            setPlayProgress(0);
        }
    }, [blob]);

    const handlePlay = () => {
        if (!blob) return;
        const audio = new Audio(URL.createObjectURL(blob));
        audioRef.current = audio;
        audio.play();
        setIsPlaying(true);

        progressTimer.current = setInterval(() => {
            if (audio.duration) setPlayProgress(audio.currentTime / audio.duration);
        }, 100);

        audio.onended = () => {
            setIsPlaying(false);
            setPlayProgress(0);
            clearInterval(progressTimer.current);
        };
    };

    const handlePause = () => {
        audioRef.current?.pause();
        setIsPlaying(false);
        clearInterval(progressTimer.current);
    };

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mt: 0.5 }}>
            {!isDone && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <IconButton
                        onClick={isRecording ? onStop : onStart}
                        sx={{
                            width: 44, height: 44,
                            backgroundColor: isRecording ? '#c0392b' : '#F9F5ED',
                            border: '2px solid #2A2A2A',
                            flexShrink: 0,
                            '&:hover': { backgroundColor: isRecording ? '#e74c3c' : 'rgba(249,245,237,0.8)' },
                        }}
                    >
                        {isRecording
                            ? <StopIcon sx={{ color: '#F9F5ED', fontSize: 20 }} />
                            : <PlayIcon sx={{ color: '#2A2A2A', fontSize: 20 }} />
                        }
                    </IconButton>

                    {isRecording && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: '2px', height: 32 }}>
                            {Array.from({ length: BAR_COUNT }).map((_, i) => (
                                <Box
                                    key={i}
                                    sx={{
                                        width: 3,
                                        borderRadius: 2,
                                        backgroundColor: '#F9F5ED',
                                        animation: `wave ${0.4 + (i % 5) * 0.1}s ease-in-out infinite alternate`,
                                        animationDelay: `${(i % 7) * 0.05}s`,
                                        '@keyframes wave': {
                                            from: { height: '4px' },
                                            to: { height: `${8 + (i % 6) * 4}px` },
                                        },
                                    }}
                                />
                            ))}
                        </Box>
                    )}
                </Box>
            )}

            {isDone && bars.length > 0 && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <IconButton
                        onClick={isPlaying ? handlePause : handlePlay}
                        sx={{
                            width: 44, height: 44,
                            backgroundColor: '#F9F5ED',
                            border: '2px solid #2A2A2A',
                            flexShrink: 0,
                            '&:hover': { backgroundColor: 'rgba(249,245,237,0.8)' },
                        }}
                    >
                        {isPlaying
                            ? <PauseIcon sx={{ color: '#2A2A2A', fontSize: 20 }} />
                            : <PlayIcon sx={{ color: '#2A2A2A', fontSize: 20 }} />
                        }
                    </IconButton>

                    <Waveform bars={bars} progress={playProgress} />

                    <IconButton
                        onClick={onRerecord}
                        disabled={isPlaying}
                        size="small"
                        sx={{
                            color: isPlaying ? 'rgba(249,245,237,0.3)' : 'rgba(249,245,237,0.7)',
                            '&:hover': { color: '#F9F5ED' },
                        }}
                    >
                        <ReplayIcon sx={{ fontSize: 20 }} />
                    </IconButton>
                </Box>
            )}
        </Box>
    );
};