export function mapApiError(error, fallback = 'Something went wrong') {
  if (!error) return { type: 'error', message: fallback };

  if (error.message === 'Network Error') {
    return { type: 'error', message: 'Network connection failed. Please try again.' };
  }

  const status = error.response?.status;
  const serverError = error.response?.data?.error || error.response?.data?.message;

  if (status === 400) return { type: 'warning', message: serverError || 'Invalid request.' };
  if (status === 401) return { type: 'warning', message: 'Session expired. Please login again.' };
  if (status === 404) return { type: 'warning', message: 'Requested resource not found.' };
  if (status >= 500) return { type: 'error', message: serverError || 'Server error occurred.' };

  return { type: 'error', message: serverError || fallback };
}
