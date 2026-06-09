import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import { Navbar } from '../../shared/ui/Navbar';
import { ExamSetup } from '../../features/exam/ui/ExamSetup';
import { ExamRecording } from '../../features/exam/ui/ExamRecording';
import { ExamResults } from '../../features/exam/ui/ExamResults';
import { RerecordModal } from '../../features/exam/ui/RerecordModal';
import { useExam } from '../../features/exam/model/useExam';

const ProcessingOverlay = ({ step }) => (
    <Box sx={{
        position: 'fixed', inset: 0, zIndex: 1500,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        backgroundColor: 'rgba(0,0,0,0.4)',
    }}>
        <Box sx={{
            backgroundColor: '#F9F5ED',
            borderRadius: '30px',
            p: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 2,
            maxWidth: 320,
            textAlign: 'center',
        }}>
            <CircularProgress sx={{ color: '#5E83AE' }} />
            <Box sx={{ fontFamily: '"Montserrat", sans-serif', fontSize: '1.2rem', color: '#2A2A2A' }}>
                {step}
            </Box>
        </Box>
    </Box>
);

export const ExamPage = () => {
    const {
        screen, setScreen,
        groups, tickets,
        selectedGroup, setSelectedGroup,
        selectedStudent, setSelectedStudent,
        ticketNumber, setTicketNumber,
        getTicketQuestions, isStudentDone, getStudentGrade,
        recordings, savedAudios, activeRecording, recordingSeconds,
        saveAudio, startRecording, stopRecording,
        rerecordModal, passphrase, setPassphrase, openRerecord, confirmRerecord, setRerecordModal,
        startExam, saveAnswers, processingStep,
        recommendedGrade, gradeComment, finalGrade, setFinalGrade,
        generateComment, generatingComment,
        saveFinalResults,
    } = useExam();

    const ticketQuestions = getTicketQuestions();

    return (
        <Box sx={{ minHeight: '100vh', backgroundColor: '#5E83AE' }}>
            <Navbar activePath="/exam" />

            <Box sx={{ px: 4, py: 15 }}>
                {(screen === 'setup') && (
                    <ExamSetup
                        groups={groups}
                        tickets={tickets}
                        isStudentDone={isStudentDone}
                        getStudentGrade={getStudentGrade}
                        selectedGroup={selectedGroup}
                        setSelectedGroup={setSelectedGroup}
                        selectedStudent={selectedStudent}
                        setSelectedStudent={setSelectedStudent}
                        ticketNumber={ticketNumber}
                        setTicketNumber={setTicketNumber}
                        ticketQuestions={ticketQuestions}
                        onStart={startExam}
                    />
                )}

                {(screen === 'recording' || screen === 'processing') && (
                    <ExamRecording
                        questions={ticketQuestions}
                        recordings={recordings}
                        savedAudios={savedAudios}
                        activeRecording={activeRecording}
                        recordingSeconds={recordingSeconds}
                        onStart={startRecording}
                        onStop={stopRecording}
                        onRerecord={openRerecord}
                        onSaveAudio={saveAudio}
                        onSave={saveAnswers}
                    />
                )}

                {screen === 'results' && (
                    <ExamResults
                        recommendedGrade={recommendedGrade}
                        gradeComment={gradeComment}
                        finalGrade={finalGrade}
                        setFinalGrade={setFinalGrade}
                        onSave={saveFinalResults}
                        onGenerateComment={generateComment}
                        generatingComment={generatingComment}
                    />
                )}
            </Box>

            {screen === 'processing' && <ProcessingOverlay step={processingStep} />}

            <RerecordModal
                open={!!rerecordModal}
                passphrase={passphrase}
                onChange={setPassphrase}
                onConfirm={confirmRerecord}
                onClose={() => setRerecordModal(null)}
            />
        </Box>
    );
};