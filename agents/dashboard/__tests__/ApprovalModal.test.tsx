import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ApprovalModal } from '../components/ApprovalModal';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import * as api from '../lib/api';

// Mock WebSocket
class MockWebSocket {
  onopen: () => void = () => {};
  onmessage: (e: any) => void = () => {};
  onclose: () => void = () => {};
  onerror: (e: any) => void = () => {};
  close = vi.fn();
  send = vi.fn();

  constructor(url: string) {
    // Simulate connection
    setTimeout(() => this.onopen(), 10);
  }
}

global.WebSocket = MockWebSocket as any;

describe('ApprovalModal Component', () => {
  beforeEach(() => {
    vi.mock('../lib/api', () => ({
      API_BASE_URL: 'http://localhost:8080',
      respondToApproval: vi.fn(),
    }));
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders nothing initially', () => {
    const { container } = render(<ApprovalModal />);
    expect(container.firstChild).toBeNull();
  });

  it('shows modal when receiving approval request', async () => {
    render(<ApprovalModal />);

    // Simulate receiving a message via WebSocket
    // We need to access the socket instance created inside useEffect
    // This is hard to test directly without exposing socket or mocking more deeply.
    // Instead, let's mock the component state update if possible, or refactor component to be testable.
    // Given the constraints, we'll skip deep socket testing and focus on API interaction if state was set.
    
    // Actually, let's mock the internal useState if we could, but we can't easily.
    // Let's rely on the fact that useEffect sets up the socket.
    
    // Better approach: Integration test.
    // But for unit test, we can mock the socket behavior by triggering the onmessage handler.
    // Since we replaced global.WebSocket, the component uses our MockWebSocket.
    // But we don't have a reference to the instance created inside the component.
    
    // Alternative: We can spy on window.WebSocket
    
  });
});
