import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import InputBase from '@mui/material/InputBase';
import { useRef } from 'react';
import { Navbar } from '../../shared/ui/Navbar';
import { GroupCard, AddGroupCard } from '../../features/students/ui/GroupCard';
import { DeleteGroupDialog } from '../../features/students/ui/DeleteGroupDialog';
import { useStudents } from '../../features/students/model/useStudents';
import Tooltip from '@mui/material/Tooltip';
import { InfoOutlined as InfoOutlinedIcon } from '@mui/icons-material';
import { StudentRow } from '../../features/students/ui/StudentRow';

const textSx = { fontFamily: '"Montserrat", sans-serif', color: '#F9F5ED' };

export const StudentsPage = () => {
    const {
        groups, selectedGroup, setSelectedGroup,
        isAdding, newGroupName, setNewGroupName, startAddGroup, handleGroupKeyDown,
        startEditGroup,
        deleteTarget, askDeleteGroup, cancelDelete, confirmDelete,
        addingStudent, newStudentName, setNewStudentName, startAddStudent, handleStudentKeyDown,
        fileInputRef, loadFromFile, saveStudents, editStudent, deleteStudent,
    } = useStudents();

    return (
        <Box sx={{ minHeight: '100vh', backgroundColor: '#5E83AE' }}>
            <Navbar activePath="/students" />

            <Box sx={{ px: { xs: 2, md: 4 }, py: { xs: 10, md: 15 } }}>
                {!selectedGroup ? (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, justifyContent: { xs: 'center', md: 'flex-start' } }}>
                        <AddGroupCard
                            isAdding={isAdding}
                            value={newGroupName}
                            onChange={(e) => setNewGroupName(e.target.value)}
                            onKeyDown={handleGroupKeyDown}
                            onStartAdd={startAddGroup}
                        />
                        {groups.map((g) => (
                            <GroupCard
                                key={g.id_group}
                                group={g}
                                onSelect={setSelectedGroup}
                                onEdit={startEditGroup}
                                onDelete={askDeleteGroup}
                            />
                        ))}
                    </Box>
                ) : (
                    <Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                            <Box
                                onClick={() => setSelectedGroup(null)}
                                sx={{ ...textSx, fontSize: '1.4rem', cursor: 'pointer', userSelect: 'none' }}
                            >
                                ← {selectedGroup.group_name}
                            </Box>
                            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                                <Tooltip
                                    title="Введите ФИО студента и нажмите Enter для добавления.
                                    Для отмены ввода можно нажать Esc. После добавления всех студентов нажмите на
                                    кнопку Сохранить."
                                    placement="bottom"
                                    arrow
                                    componentsProps={{
                                        tooltip: {
                                            sx: {
                                                backgroundColor: '#F9F5ED',
                                                color: '#2A2A2A',
                                                fontFamily: '"Montserrat", sans-serif',
                                                fontSize: '0.9rem',
                                            },
                                        },
                                        arrow: {
                                            sx: {
                                                color: '#F9F5ED',
                                            },
                                        },
                                    }}
                                >
                                    <InfoOutlinedIcon sx={{ color: '#F9F5ED', cursor: 'pointer', fontSize: 24 }} />
                                </Tooltip>
                                <Button
                                    variant="outlined"
                                    disabled={!selectedGroup?.students?.some((s) => s.pending)}
                                    onClick={saveStudents}
                                    sx={{
                                        fontFamily: '"Montserrat", sans-serif',
                                        fontWeight: '400',
                                        fontSize: '1.2rem',
                                        borderRadius: '20px',
                                        textTransform: 'none',
                                        backgroundColor: '#F9F5ED',
                                        borderColor: '#2A2A2A',
                                        color: '#2A2A2A',
                                        '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)', borderColor: '#F9F5ED' },
                                        '&.Mui-disabled': { borderColor: 'rgba(249,245,237,0.3)', color: 'rgba(249,245,237,0.3)', backgroundColor: 'transparent' },
                                    }}
                                >
                                    Сохранить
                                </Button>
                                <Button
                                    variant="outlined"
                                    onClick={startAddStudent}
                                    sx={{
                                        ...textSx,
                                        fontFamily: '"Montserrat", sans-serif',
                                        fontWeight: '400',
                                        backgroundColor: '#F9F5ED',
                                        borderColor: '#2A2A2A',
                                        color: '#2A2A2A',
                                        fontSize: '1.2rem',
                                        borderRadius: '20px',
                                        textTransform: 'none',
                                        '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)', borderColor: '#F9F5ED' },
                                    }}
                                >
                                    Добавить студента
                                </Button>
                                <Button
                                    variant="outlined"
                                    onClick={() => fileInputRef.current?.click()}
                                    sx={{
                                        ...textSx,
                                        fontFamily: '"Montserrat", sans-serif',
                                        fontWeight: '400',
                                        backgroundColor: '#F9F5ED',
                                        borderColor: '#2A2A2A',
                                        color: '#2A2A2A',
                                        fontSize: '1.2rem',
                                        borderRadius: '20px',
                                        textTransform: 'none',
                                        '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)', borderColor: '#F9F5ED' },
                                    }}
                                >
                                    Загрузить из файла
                                </Button>
                                <input ref={fileInputRef} type="file" accept=".docx,.pdf" hidden onChange={loadFromFile} />
                            </Box>
                        </Box>

                        <Box sx={{ m: 0, display: 'flex', flexDirection: 'column' }}>
                            {[...selectedGroup.students]
                                .sort((a, b) => a.name.localeCompare(b.name, 'ru'))
                                .map((s, i) => (
                                <StudentRow
                                    key={s.id}
                                    index={i + 1}
                                    student={s}
                                    onEdit={editStudent}
                                    onDelete={deleteStudent}
                                />
                            ))}
                            {addingStudent && (
                                <Box sx={{ fontSize: '1.2rem', py: 0.5, minWidth: '400px', color: '#F9F5ED' }}>
                                    <InputBase
                                        autoFocus
                                        value={newStudentName}
                                        onChange={(e) => setNewStudentName(e.target.value)}
                                        onKeyDown={handleStudentKeyDown}
                                        onBlur={() => setAddingStudent(false)}
                                        placeholder="ФИО студента"
                                        sx={{
                                            fontFamily: '"Montserrat", sans-serif',
                                            color: '#F9F5ED',
                                            fontSize: '1.2rem',
                                            minWidth: '400px',
                                            maxWidth: '1000px',
                                        }}
                                    />
                                </Box>
                            )}
                        </Box>
                    </Box>
                )}
            </Box>

            <DeleteGroupDialog
                open={!!deleteTarget}
                onConfirm={confirmDelete}
                onCancel={cancelDelete}
            />
        </Box>
    );
};