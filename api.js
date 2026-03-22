const BASE_URL = "https://my-travel-buddy-kn22.onrender.com/api";

export const forgotPassword = async (email) => {
    const response = await fetch(`${BASE_URL}/auth/forgot-password`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
    });
    return response;
};
