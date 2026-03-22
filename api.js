'use strict';

const BASE_URL = 'https://api.example.com';

function forgotPassword(email) {
    const url = `${BASE_URL}/auth/forgot-password`;
    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
    }).then(response => {
        if (!response.ok) {
            throw new Error('Failed to send forgot password email');
        }
        return response.json();
    });
}

module.exports = { forgotPassword };