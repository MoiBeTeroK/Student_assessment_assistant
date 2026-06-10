import Box from '@mui/material/Box';
import { Navbar } from '../../shared/ui/Navbar';
import { SettingsForm } from '../../features/settings/ui/SettingsForm';

export const SettingsPage = () => {
    return (
        <Box sx={{ minHeight: '100vh', backgroundColor: '#5E83AE' }}>
            <Navbar activePath="/settings" />

            <Box sx={{ pt: { xs: 10, md: 14 }, px: { xs: 2, md: 4 } }}>
                <SettingsForm currentUser="admin"/>
            </Box>
        </Box>
    );
};