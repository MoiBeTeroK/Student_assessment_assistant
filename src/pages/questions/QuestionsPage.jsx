import { useState } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import { Navbar } from '../../shared/ui/Navbar';
import { QuestionRow } from '../../features/questions/ui/QuestionRow';
import { AddQuestionModal } from '../../features/questions/ui/AddQuestionModal';
import { useQuestions } from '../../features/questions/model/useQuestions';
import { gigachatApi } from '../../shared/api/gigachatApi';

const btnSx = {
    fontFamily: '"Montserrat", sans-serif',
    fontWeight: '400',
    backgroundColor: '#F9F5ED',
    borderColor: '#2A2A2A',
    color: '#2A2A2A',
    borderRadius: '20px',
    textTransform: 'none',
    fontSize: '1.2rem',
    '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)', borderColor: '#F9F5ED' },
};

export const QuestionsPage = () => {
    const [exportAnchor, setExportAnchor] = useState(null);

    const {
        questions, pendingQuestions, setPendingQuestions, disciplineId,
        addModalOpen, setAddModalOpen,
        editModalOpen, setEditModalOpen,
        editingQuestion,
        addQuestion, openEdit, saveEdit, deleteQuestion,
        fileInputRef, loadFromFile,
        savePending, cancelPending,
        exportQuestions, clearAllQuestions,
    } = useQuestions();

    const hasPending = pendingQuestions.length > 0;

    return (
        <Box sx={{ minHeight: '100vh', backgroundColor: '#5E83AE' }}>
            <Navbar activePath="/questions" />

            <Box sx={{ px: 4, py: 15 }}>
                {!disciplineId ? (
                    <Box sx={{
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        height: '40vh',
                        fontFamily: '"Montserrat", sans-serif',
                        color: '#F9F5ED',
                        fontSize: '1.2rem',
                        textAlign: 'center',
                    }}>
                        Выберите активную дисциплину в настройках
                    </Box>
                ) : (
                    <>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
                            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                                {!hasPending && (
                                    <>
                                        <Button variant="outlined" onClick={() => fileInputRef.current?.click()} sx={btnSx}>
                                            Загрузить вопросы из файла
                                        </Button>
                                        <input ref={fileInputRef} type="file" accept=".docx,.pdf,.txt" hidden onChange={loadFromFile} />
                                    </>
                                )}
                                <Button variant="outlined" onClick={() => setAddModalOpen(true)} sx={btnSx}>
                                    Добавить вопрос вручную
                                </Button>
                                {!hasPending && (
                                    <>
                                        <Button variant="outlined" onClick={(e) => setExportAnchor(e.currentTarget)} sx={btnSx}>
                                            Экспорт вопросов
                                        </Button>
                                        <Menu
                                            anchorEl={exportAnchor}
                                            open={Boolean(exportAnchor)}
                                            onClose={() => setExportAnchor(null)}
                                        >
                                            <MenuItem onClick={() => { exportQuestions('docx'); setExportAnchor(null); }}>DOCX</MenuItem>
                                            <MenuItem onClick={() => { exportQuestions('pdf'); setExportAnchor(null); }}>PDF</MenuItem>
                                        </Menu>
                                    </>
                                )}
                                {!hasPending && (
                                    <Button variant="outlined" onClick={clearAllQuestions} sx={btnSx}>
                                        Удалить все вопросы
                                    </Button>
                                )}
                            </Box>

                            {hasPending && (
                                <Box sx={{ display: 'flex', gap: 2 }}>
                                    <Button variant="outlined" onClick={savePending} sx={btnSx}>
                                        Сохранить
                                    </Button>
                                    <Button
                                        variant="outlined"
                                        onClick={cancelPending}
                                        sx={{ ...btnSx, backgroundColor: 'transparent', color: '#F9F5ED', borderColor: '#F9F5ED' }}
                                    >
                                        Отмена
                                    </Button>
                                </Box>
                            )}

                            {hasPending && (
                                <Box sx={{ fontFamily: '"Montserrat", sans-serif', color: '#F9F5ED', fontSize: '1.2rem', minWidth: 160, textAlign: 'center' }}>
                                    Весовые коэффициенты
                                </Box>
                            )}
                        </Box>

                        {questions.length === 0 && !hasPending && (
                            <Box sx={{
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                height: '40vh',
                                fontFamily: '"Montserrat", sans-serif',
                                color: '#F9F5ED',
                                fontSize: '1.2rem',
                                textAlign: 'center',
                            }}>
                                На данный момент<br />вопросов нет
                            </Box>
                        )}

                        <Box>
                            {questions.map((q, i) => (
                                <QuestionRow
                                    key={q.id_question}
                                    index={i + 1}
                                    question={q}
                                    onEdit={openEdit}
                                    onDelete={deleteQuestion}
                                    weightColumn={hasPending}
                                />
                            ))}
                            {pendingQuestions.map((q, i) => (
                                <QuestionRow
                                    key={q._tempId}
                                    index={questions.length + i + 1}
                                    question={q}
                                    onDelete={() => setPendingQuestions((prev) => prev.filter((p) => p._tempId !== q._tempId))}
                                    weightColumn={true}
                                />
                            ))}
                        </Box>
                    </>
                )}
            </Box>

            <AddQuestionModal
                open={addModalOpen}
                onClose={() => setAddModalOpen(false)}
                onSave={addQuestion}
                onGenerateAnswer={(text) => gigachatApi.generateAnswerByText(text, disciplineId).then((r) => r.text)}
                title="Добавление вопроса"
            />

            <AddQuestionModal
                key={editingQuestion?.id_question ?? 'edit'}
                open={editModalOpen}
                onClose={() => setEditModalOpen(false)}
                onSave={saveEdit}
                onGenerateAnswer={(text) => gigachatApi.generateAnswerByText(text, disciplineId).then((r) => r.text)}
                initialData={editingQuestion}
                title="Редактирование вопроса"
            />
        </Box>
    );
};
