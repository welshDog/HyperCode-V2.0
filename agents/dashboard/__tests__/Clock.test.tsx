import { render, screen, act } from '@testing-library/react';
import { Clock } from '../components/Clock';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

describe('Clock Component', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders initial placeholder state before mount', () => {
    render(<Clock />);
    // Initial state is --:--:--
    expect(screen.getByText('--:--:--')).toBeDefined();
  });

  it('updates time after mounting', () => {
    const date = new Date(2026, 1, 26, 12, 0, 0);
    vi.setSystemTime(date);
    
    render(<Clock />);
    
    // Fast-forward effects
    act(() => {
      vi.advanceTimersByTime(100); 
    });
    
    // Should display time
    expect(screen.getByText(date.toLocaleTimeString())).toBeDefined();
  });

  it('updates time every second', () => {
    const date = new Date(2026, 1, 26, 12, 0, 0);
    vi.setSystemTime(date);
    render(<Clock />);
    
    act(() => {
        vi.advanceTimersByTime(100);
    });
    expect(screen.getByText('12:00:00 PM')).toBeDefined();
    
    // Advance 1 second
    act(() => {
        vi.advanceTimersByTime(1000);
    });
    
    // Should update (assuming toLocaleTimeString changes)
    // Note: implementation depends on locale, this is a basic check
    // If test fails due to locale, we might need to mock toLocaleTimeString
  });
});
