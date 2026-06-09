import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import { RecordButton } from './RecordButton';

const textSx = { fontFamily: '"Montserrat", sans-serif', color: '#F9F5ED' };

export const ExamRecording = ({ questions, recordings, savedAudios, activeRecording, recordingSeconds, onStart, onStop, onRerecord, onSaveAudio, onSave }) => {
    const allSaved = questions.length > 0 && questions.every((q) => savedAudios?.has(q.id));

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
            <Box sx={{ ...textSx, fontSize: '1.2rem', mb: 0.5 }}>Вопросы в билете:</Box>

            {questions.map((q, i) => {
                const rec = recordings[q.id];
                const isRecording = activeRecording === q.id;

                return (
                    <Box key={q.id} sx={{ mb: 2 }}>
                        <Box sx={{ ...textSx, fontSize: '1.1rem', mb: 2 }}>{i + 1}. {q.name}</Box>
                        <RecordButton
                            questionId={q.id}
                            isRecording={isRecording}
                            isDone={!!rec}
                            duration={rec?.duration ?? 0}
                            currentSeconds={isRecording ? recordingSeconds : 0}
                            onStart={() => onStart(q.id)}
                            onStop={onStop}
                            onRerecord={() => onRerecord(q.id)}
                            onSaveAudio={() => onSaveAudio(q.id)}
                            isSaved={savedAudios?.has(q.id) ?? false}
                            blob={rec?.blob ?? null}
                        />
                    </Box>
                );
            })}

            <Button
                variant="outlined"
                onClick={onSave}
                disabled={!allSaved}
                sx={{
                    fontFamily: '"Montserrat", sans-serif',
                    fontWeight: '400',
                    backgroundColor: allSaved ? '#F9F5ED' : 'transparent',
                    borderColor: allSaved ? '#2A2A2A' : 'rgba(249,245,237,0.4)',
                    color: allSaved ? '#2A2A2A' : 'rgba(249,245,237,0.4)',
                    borderRadius: '20px',
                    textTransform: 'none',
                    fontSize: '1.2rem',
                    width: 'fit-content',
                    '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)', borderColor: '#F9F5ED' },
                    '&.Mui-disabled': { borderColor: 'rgba(249,245,237,0.3)', color: 'rgba(249,245,237,0.3)' },
                }}
            >
                Сохранить ответы студента
            </Button>
        </Box>
    );
};