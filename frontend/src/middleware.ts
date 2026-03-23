import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PROTECTED_ROUTES = ['/', '/alerts', '/incidents', '/exposures', '/copilot', '/policies', '/knowledge', '/settings'];
const AUTH_ROUTES = ['/login'];

export function middleware(request: NextRequest) {
  const token = request.cookies.get('aisec_token')?.value;
  const { pathname } = request.nextUrl;

  // 1. Redirect to login if accessing protected route without token
  if (!token && PROTECTED_ROUTES.some(route => pathname === route || pathname.startsWith(route + '/'))) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // 2. Redirect to dashboard if accessing auth route with valid token
  if (token && AUTH_ROUTES.includes(pathname)) {
    return NextResponse.redirect(new URL('/', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
