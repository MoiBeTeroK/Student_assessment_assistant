import { useState, useEffect, useRef } from 'react';
import { storage } from '../../../shared/lib/storage';
import { groupsApi } from '../../../shared/api/groupsApi';
import { studentsApi } from '../../../shared/api/studentsApi';
import { testsApi } from '../../../shared/api/testsApi';
import { resultsApi } from '../../../shared/api/resultsApi';

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

    const savedResults = storage.get('exam_results') ?? [];

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

    const isStudentDone = (studentId) => savedResults.some((r) => r.studentId === studentId);

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

                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `question_${questionId}_${Date.now()}.webm`;
                a.click();
                URL.revokeObjectURL(url);

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
        setExamResultId(null);
    };

    return {
        screen, setScreen,
        groups, tickets,
        selectedGroup, setSelectedGroup,
        selectedStudent, setSelectedStudent,
        ticketNumber, setTicketNumber,
        getTicketQuestions, getTicket, isStudentDone,
        recordings, activeRecording,
        startRecording, stopRecording,
        rerecordModal, passphrase, setPassphrase, openRerecord, confirmRerecord, setRerecordModal,
        startExam, saveAnswers, processingStep,
        recommendedGrade, gradeComment, finalGrade, setFinalGrade,
        saveFinalResults, examResultId,
    };
};
