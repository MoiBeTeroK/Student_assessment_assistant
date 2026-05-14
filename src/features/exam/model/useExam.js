import { useState, useRef } from 'react';
import { storage } from '../../../shared/lib/storage';

export const useExam = () => {
    const [selectedGroup, setSelectedGroup] = useState(null);
    const [selectedStudent, setSelectedStudent] = useState(null);
    const [ticketNumber, setTicketNumber] = useState('');
    const [screen, setScreen] = useState('setup');

    const [recordings, setRecordings] = useState({});
    const [activeRecording, setActiveRecording] = useState(null);
    const mediaRecorderRef = useRef(null);
    const chunksRef = useRef([]);
    const timerRef = useRef(null);

    const [rerecordModal, setRerecordModal] = useState(null);
    const [passphrase, setPassphrase] = useState('');
    const PASSPHRASE = 'reset';

    const [processingStep, setProcessingStep] = useState('');
    const [recommendedGrade, setRecommendedGrade] = useState(null);
    const [gradeComment, setGradeComment] = useState('');
    const [finalGrade, setFinalGrade] = useState('');

    const groups = storage.get('students_data')?.groups ?? [];
    const tickets = storage.get('tickets_data')?.tickets ?? [];
    const questions = storage.get('questions_data')?.questions ?? [];
    const savedResults = storage.get('exam_results') ?? [];

    const getTicket = () => tickets.find((t) => t.name === `Билет №${ticketNumber}`);

    const getTicketQuestions = () => {
        const ticket = getTicket();
        if (!ticket) return [];
        return ticket.questionIds.map((id) => questions.find((q) => q.id === id)).filter(Boolean);
    };

    const isStudentDone = (studentId) => savedResults.some((r) => r.studentId === studentId);

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

            mr.onstop = () => {
                const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
                setRecordings((prev) => ({ ...prev, [questionId]: { blob } }));
                stream.getTracks().forEach((t) => t.stop());
                clearInterval(timerRef.current);
                setActiveRecording(null);
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

    const confirmRerecord = () => {
        if (passphrase !== PASSPHRASE) return;
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
            setProcessingStep('Сохранение записей в облако...');
            await new Promise((r) => setTimeout(r, 1000));

            setProcessingStep('Расшифровка ответов...');
            await new Promise((r) => setTimeout(r, 1200));

            setProcessingStep('Подсчёт рекомендуемой оценки...');
            await new Promise((r) => setTimeout(r, 1000));
            setRecommendedGrade(4);

            setProcessingStep('Получение комментария...');
            await new Promise((r) => setTimeout(r, 800));
            setGradeComment('Студент продемонстрировал хорошее знание материала. Ответы были полными, однако местами не хватало конкретных примеров.');
            setFinalGrade('4');

            setScreen('results');
        } catch {
            setScreen('recording');
        }
    };

    const saveFinalResults = async () => {
        const results = [...savedResults, {
            studentId: selectedStudent.id,
            grade: finalGrade,
            ticketNumber,
        }];
        storage.set('exam_results', results);

        setScreen('setup');
        setSelectedGroup(null);
        setSelectedStudent(null);
        setTicketNumber('');
        setRecordings({});
        setRecommendedGrade(null);
        setGradeComment('');
        setFinalGrade('');
    };

    return {
        screen, setScreen,
        groups, tickets, questions,
        selectedGroup, setSelectedGroup,
        selectedStudent, setSelectedStudent,
        ticketNumber, setTicketNumber,
        getTicketQuestions, getTicket, isStudentDone,
        recordings, activeRecording,
        startRecording, stopRecording,
        rerecordModal, passphrase, setPassphrase, openRerecord, confirmRerecord, setRerecordModal,
        saveAnswers, processingStep,
        recommendedGrade, gradeComment, finalGrade, setFinalGrade,
        saveFinalResults,
    };
};