import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import { Navbar } from '../../shared/ui/Navbar';
import { QuestionRow } from '../../features/questions/ui/QuestionRow';
import { AddQuestionModal } from '../../features/questions/ui/AddQuestionModal';
import { useQuestions } from '../../features/questions/model/useQuestions';

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
    const {
        questions, pendingQuestions,
        addModalOpen, setAddModalOpen,
        editModalOpen, setEditModalOpen,
        editingQuestion,
        addQuestion, openEdit, saveEdit, deleteQuestion,
        fileInputRef, loadFromFile,
        savePending, cancelPending,
    } = useQuestions();

    const hasPending = pendingQuestions.length > 0;
    const allQuestions = [...questions, ...pendingQuestions];

    return (
        <Box sx={{ minHeight: '100vh', backgroundColor: '#5E83AE' }}>
            <Navbar activePath="/questions" />

            <Box sx={{ px: 4, py: 15 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
                    <Box sx={{ display: 'flex', gap: 2 }}>
                        {!hasPending && (
                            <>
                                <Button variant="outlined" onClick={() => fileInputRef.current?.click()} sx={btnSx}>
                                    Загрузить вопросы из файла
                                </Button>
                                <input ref={fileInputRef} type="file" accept=".txt" hidden onChange={loadFromFile} />
                            </>
                        )}
                        <Button variant="outlined" onClick={() => setAddModalOpen(true)} sx={btnSx}>
                            Добавить вопрос вручную
                        </Button>
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

                {allQuestions.length === 0 && (
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
                            key={q.id}
                            index={i + 1}
                            question={q}
                            onEdit={openEdit}
                            onDelete={deleteQuestion}
                            weightColumn={hasPending}
                        />
                    ))}
                    {pendingQuestions.map((q, i) => (
                        <QuestionRow
                            key={q.id}
                            index={questions.length + i + 1}
                            question={q}
                            onDelete={(id) => cancelPending()}
                            weightColumn={true}
                        />
                    ))}
                </Box>
            </Box>

            <AddQuestionModal
                open={addModalOpen}
                onClose={() => setAddModalOpen(false)}
                onSave={addQuestion}
                title="Добавление вопроса"
            />

            <AddQuestionModal
                key={editingQuestion?.id ?? 'edit'}
                open={editModalOpen}
                onClose={() => setEditModalOpen(false)}
                onSave={saveEdit}
                initialData={editingQuestion}
                title="Редактирование вопроса"
            />
        </Box>
    );
};