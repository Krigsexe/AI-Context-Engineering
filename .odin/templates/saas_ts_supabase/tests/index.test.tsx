// tests/index.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import Home from '../src/pages/index';

describe('Home Page', () => {
  test('renders welcome message', () => {
    render(<Home />);
    const welcomeMessage = screen.getByText(/Welcome to your Next.js \+ Supabase boilerplate!/i);
    expect(welcomeMessage).toBeInTheDocument();
  });

  test('has login button', () => {
    render(<Home />);
    const button = screen.getByRole('button', { name: /login with github/i });
    expect(button).toBeInTheDocument();
  });

  test('login button click simulates OAuth flow', async () => {
    render(<Home />);
    const button = screen.getByRole('button', { name: /login with github/i });
    fireEvent.click(button);
    // Mock Supabase authentication function here for test purposes
    // Test should ensure login function is called
  });
});
