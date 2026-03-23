"use client";

export async function handleApiError(error: any) {
  console.error('[API Error]:', error);
  
  // In a real app, this might trigger a toast notification or global alert
  let message = 'An unexpected error occurred in the security gateway.';
  
  if (error instanceof Response) {
    try {
      const data = await error.json();
      message = data.detail || message;
    } catch {
      // JSON parsing failed, use default message
    }
  } else if (error instanceof Error) {
    message = error.message;
  }
  
  return { error: true, message };
}
