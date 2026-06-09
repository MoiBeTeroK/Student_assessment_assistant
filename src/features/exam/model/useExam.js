import { useState, useEffect, useRef } from 'react';
import { storage } from '../../../shared/lib/storage';
import { convertToWav } from '../../../shared/lib/convertToWav';
import { useAuth } from '../../../app/AuthContext';
import { groupsApi } from '../../../shared/api/groupsApi';
import { studentsApi, usersApi } from '../../../shared/api/studentsApi';
import { testsApi } from '../../../shared/api/testsApi';
import { resultsApi } from '../../../shared/api/resultsApi';
import { storageApi } from '../../../shared/api/storageApi';
import { gigachatApi } from '../../../shared/api/gigachatApi';

const getActiveDisciplineId = () => storage.get('settings_admin')?.activeDisciplineId ?? null;

export const useExam = () => {
    const [selectedGroup, setSelectedGroup] = useState(null);
    const [selectedStudent, setSelectedStudent] = useState(null);
    const [ticketNumber, setTicketNumber] = useState('');
    const [screen, setScreen] = useState('setup');
    const [examResultId, setExamResultId] = useState(null);

    const [groups, setGroups] = useState([]);
    const [tickets, setTickets] = useState([]);

    const [recordings, setRecordings] = useState({});
    const [savedAudios, setSavedAudios] = useState(new Set());
    const [activeRecording, setActiveRecording] = useState(null);
    const mediaRecorderRef = useRef(null);
    const chunksRef = useRef([]);
    const timerRef = useRef(null);

    const { user } = useAuth();

    const [rerecordModal, setRerecordModal] = useState(null);
    const [passphrase, setPassphrase] = useState('');

    const [processingStep, setProcessingStep] = useState('');
    const [recommendedGrade, setRecommendedGrade] = useState(null);
    const [gradeComment, setGradeComment] = useState('');
    const [finalGrade, setFinalGrade] = useState('');
    const [generatingComment, setGeneratingComment] = useState(false);

    const [examResults, setExamResults] = useState([]);

    useEffect(() => {
        Promise.all([groupsApi.getAll(), studentsApi.getAll()])
            .then(([groupsData, studentsData]) => {
                const transformed = groupsData.map((g) => ({
                    id: g.id_group,
                    name: g.group_name,
                    students: studentsData
                        .filter((s) => {
                            const grp = s.group_rel ?? s.group;
                            return grp?.id_group === g.id_group;
                        })
                        .map((s) => ({ id: s.id_student, name: s.name }))
                        .sort((a, b) => a.name.localeCompare(b.name, 'ru')),
                }));
                setGroups(transformed);
            })
            .catch(() => {});
    }, []);

    useEffect(() => {
        const disciplineId = getActiveDisciplineId();
        if (!disciplineId) return;
        const year = new Date().getFullYear();
        resultsApi.getByDisciplineAndYear(disciplineId, year)
            .then(setExamResults)
            .catch(() => {});
    }, []);

    useEffect(() => {
        const disciplineId = getActiveDisciplineId();
        if (!disciplineId) return;
        testsApi.getByDiscipline(disciplineId)
            .then((data) => {
                setTickets(data.map((t) => ({
                    id: t.id_test,
                    name: `Билет №${t.test_number}`,
                    questions: t.questions,
                })));
            })
            .catch(() => {});
    }, []);

    const getTicket = () => tickets.find((t) => t.name === `Билет №${ticketNumber}`);

    const getTicketQuestions = () => {
        const ticket = getTicket();
        if (!ticket) return [];
        return ticket.questions.map((q) => ({
            id: q.id_question,
            name: q.question_content,
            standard_answer: q.standard_answer,
        }));
    };

    const isStudentDone = (studentId) =>
        examResults.some((r) => r.id_student === studentId && r.final_grade >= 3);

    const getStudentGrade = (studentId) => {
        const result = examResults.find((r) => r.id_student === studentId && r.final_grade >= 3);
        return result?.final_grade ?? null;
    };

    // --- Старт экзамена ---
    const startExam = async () => {
        const ticket = getTicket();
        if (!ticket || !selectedStudent) return;
        try {
            const result = await resultsApi.start(selectedStudent.id, ticket.id);
            setExamResultId(result.id_result);
            setScreen('recording');
        } catch (e) {
            alert(e.message || 'Ошибка при старте экзамена');
        }
    };

    // --- Сохранение аудио ---
    const saveAudio = async (questionId) => {
        const rec = recordings[questionId];
        if (!rec?.blob || !examResultId) return;
        try {
            await storageApi.processAudio(questionId, examResultId, rec.blob);
            setSavedAudios((prev) => new Set([...prev, questionId]));
        } catch (e) {
            alert(e.message || 'Ошибка при сохранении аудио');
        }
    };

    // --- Запись ---
    const startRecording = async (questionId) => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            chunksRef.current = [];
            const mr = new MediaRecorder(stream);
            mediaRecorderRef.current = mr;

            mr.ondataavailable = (e) => {
                if (e.data.size > 0) chunksRef.current.push(e.data);
            };

            mr.onstop = async () => {
                const webmBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
                stream.getTracks().forEach((t) => t.stop());
                clearInterval(timerRef.current);
                setActiveRecording(null);

                const wavBlob = await convertToWav(webmBlob);

                setRecordings((prev) => ({ ...prev, [questionId]: { blob: wavBlob } }));

                const url = URL.createObjectURL(wavBlob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `question_${questionId}_${Date.now()}.wav`;
                a.click();
                URL.revokeObjectURL(url);
            };

            mr.start();
            setActiveRecording(questionId);
        } catch {
            alert('Нет доступа к микрофону');
        }
    };

    const stopRecording = () => {
        mediaRecorderRef.current?.stop();
        clearInterval(timerRef.current);
    };

    // --- Перезапись ---
    const openRerecord = (questionId) => {
        setRerecordModal(questionId);
        setPassphrase('');
    };

    const confirmRerecord = async () => {
        try {
            const me = await usersApi.getMe();
            if (!me.passphrase || passphrase !== me.passphrase) return;
        } catch {
            return;
        }
        setRecordings((prev) => {
            const next = { ...prev };
            delete next[rerecordModal];
            return next;
        });
        setRerecordModal(null);
        setPassphrase('');
    };

    // --- Сохранение и обработка ---
    const saveAnswers = async () => {
        setScreen('processing');
        try {
            setProcessingStep('Подсчёт рекомендуемой оценки...');
            const result = await resultsApi.calculate(examResultId);
            setRecommendedGrade(result.rec_grade);
            setScreen('results');
        } catch (e) {
            alert(e.message || 'Ошибка при подсчёте оценки');
            setScreen('recording');
        }
    };

    const generateComment = async () => {
        if (!examResultId) return;
        setGeneratingComment(true);
        try {
            const { text } = await gigachatApi.generateComment(examResultId);
            setGradeComment(text);
        } catch (e) {
            alert(e.message || 'Ошибка генерации комментария');
        } finally {
            setGeneratingComment(false);
        }
    };

    const saveFinalResults = async () => {
        try {
            await resultsApi.setFinalGrade(examResultId, parseFloat(finalGrade));
        } catch (e) {
            alert(e.message || 'Ошибка при сохранении оценки');
            return;
        }
        setScreen('setup');
        setSelectedGroup(null);
        setSelectedStudent(null);
        setTicketNumber('');
        setRecordings({});
        setSavedAudios(new Set());
        setRecommendedGrade(null);
        setGradeComment('');
        setFinalGrade('');
        setExamResultId(null);
    };

    return {
        screen, setScreen,
        groups, tickets,
        selectedGroup, setSelectedGroup,
        selectedStudent, setSelectedStudent,
        ticketNumber, setTicketNumber,
        getTicketQuestions, getTicket, isStudentDone, getStudentGrade,
        recordings, savedAudios, activeRecording,
        saveAudio, startRecording, stopRecording,
        rerecordModal, passphrase, setPassphrase, openRerecord, confirmRerecord, setRerecordModal,
        startExam, saveAnswers, processingStep,
        recommendedGrade, gradeComment, finalGrade, setFinalGrade,
        generateComment, generatingComment,
        saveFinalResults, examResultId,
    };
};
