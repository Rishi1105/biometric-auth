/**
 * Behavior Service
 * Handles behavioral monitoring for continuous authentication
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

class BehaviorService {
  constructor() {
    this.monitoringActive = false;
    this.userId = null;
    this.token = null;
    this.keystrokeBuffer = [];
    this.mouseBuffer = [];
    this.deviceBuffer = [];
    this.bufferSize = 20; // Number of events to buffer before sending
    this.flushInterval = 5000; // Flush buffer every 5 seconds
    
    // Intervals for periodic data sending
    this.keystrokeInterval = null;
    this.mouseInterval = null;
    this.deviceInterval = null;
  }

  /**
   * Start keystroke monitoring
   * @param {string} userId - User ID
   * @param {string} token - Authentication token
   */
  startKeystrokeMonitoring(userId, token) {
    if (this.keystrokeInterval) return;
    
    this.userId = userId;
    this.token = token;
    this.monitoringActive = true;
    
    // Set up keystroke event listeners
    document.addEventListener('keydown', this.handleKeyDown);
    document.addEventListener('keyup', this.handleKeyUp);
    
    // Set up interval to periodically send data
    this.keystrokeInterval = setInterval(() => {
      this.flushKeystrokeBuffer();
    }, this.flushInterval);
    
    console.log('Keystroke monitoring started');
  }

  /**
   * Handle keydown events
   * @param {KeyboardEvent} event - Keyboard event
   */
  handleKeyDown = (event) => {
    if (!this.monitoringActive) return;
    
    // Don't capture actual key values for privacy, just metadata
    const keystrokeData = {
      type: 'keydown',
      timestamp: Date.now(),
      keyCode: event.keyCode,
      shift: event.shiftKey,
      ctrl: event.ctrlKey,
      alt: event.altKey,
      meta: event.metaKey
    };
    
    this.keystrokeBuffer.push(keystrokeData);
    
    // If buffer reaches threshold, send data
    if (this.keystrokeBuffer.length >= this.bufferSize) {
      this.flushKeystrokeBuffer();
    }
  };

  /**
   * Handle keyup events
   * @param {KeyboardEvent} event - Keyboard event
   */
  handleKeyUp = (event) => {
    if (!this.monitoringActive) return;
    
    const keystrokeData = {
      type: 'keyup',
      timestamp: Date.now(),
      keyCode: event.keyCode,
      shift: event.shiftKey,
      ctrl: event.ctrlKey,
      alt: event.altKey,
      meta: event.metaKey
    };
    
    this.keystrokeBuffer.push(keystrokeData);
    
    // If buffer reaches threshold, send data
    if (this.keystrokeBuffer.length >= this.bufferSize) {
      this.flushKeystrokeBuffer();
    }
  };

  /**
   * Send keystroke data to the server
   */
  async flushKeystrokeBuffer() {
    if (this.keystrokeBuffer.length === 0) return;
    
    const dataToSend = [...this.keystrokeBuffer];
    this.keystrokeBuffer = [];
    
    try {
      await fetch(`${API_BASE_URL}/behavior/keystroke`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`,
        },
        body: JSON.stringify({
          userId: this.userId,
          data: dataToSend
        }),
      });
    } catch (error) {
      console.error('Error sending keystroke data:', error);
    }
  }

  /**
   * Stop keystroke monitoring
   */
  stopKeystrokeMonitoring() {
    document.removeEventListener('keydown', this.handleKeyDown);
    document.removeEventListener('keyup', this.handleKeyUp);
    
    if (this.keystrokeInterval) {
      clearInterval(this.keystrokeInterval);
      this.keystrokeInterval = null;
    }
    
    // Flush any remaining data
    this.flushKeystrokeBuffer();
    
    console.log('Keystroke monitoring stopped');
  }

  /**
   * Start mouse movement monitoring
   * @param {string} userId - User ID
   * @param {string} token - Authentication token
   */
  startMouseMonitoring(userId, token) {
    if (this.mouseInterval) return;
    
    this.userId = userId;
    this.token = token;
    this.monitoringActive = true;
    
    // Set up mouse event listeners
    document.addEventListener('mousemove', this.handleMouseMove);
    document.addEventListener('click', this.handleMouseClick);
    
    // Set up interval to periodically send data
    this.mouseInterval = setInterval(() => {
      this.flushMouseBuffer();
    }, this.flushInterval);
    
    console.log('Mouse monitoring started');
  }

  /**
   * Handle mouse movement events
   * @param {MouseEvent} event - Mouse event
   */
  handleMouseMove = (event) => {
    if (!this.monitoringActive) return;
    
    // Throttle mouse move events to reduce data volume
    if (this.lastMouseMove && Date.now() - this.lastMouseMove < 100) {
      return;
    }
    
    this.lastMouseMove = Date.now();
    
    const mouseData = {
      type: 'mousemove',
      timestamp: Date.now(),
      x: event.clientX,
      y: event.clientY,
      screenX: event.screenX,
      screenY: event.screenY
    };
    
    this.mouseBuffer.push(mouseData);
    
    // If buffer reaches threshold, send data
    if (this.mouseBuffer.length >= this.bufferSize) {
      this.flushMouseBuffer();
    }
  };

  /**
   * Handle mouse click events
   * @param {MouseEvent} event - Mouse event
   */
  handleMouseClick = (event) => {
    if (!this.monitoringActive) return;
    
    const mouseData = {
      type: 'click',
      timestamp: Date.now(),
      x: event.clientX,
      y: event.clientY,
      button: event.button
    };
    
    this.mouseBuffer.push(mouseData);
    
    // If buffer reaches threshold, send data
    if (this.mouseBuffer.length >= this.bufferSize) {
      this.flushMouseBuffer();
    }
  };

  /**
   * Send mouse data to the server
   */
  async flushMouseBuffer() {
    if (this.mouseBuffer.length === 0) return;
    
    const dataToSend = [...this.mouseBuffer];
    this.mouseBuffer = [];
    
    try {
      await fetch(`${API_BASE_URL}/behavior/mouse`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`,
        },
        body: JSON.stringify({
          userId: this.userId,
          data: dataToSend
        }),
      });
    } catch (error) {
      console.error('Error sending mouse data:', error);
    }
  }

  /**
   * Stop mouse monitoring
   */
  stopMouseMonitoring() {
    document.removeEventListener('mousemove', this.handleMouseMove);
    document.removeEventListener('click', this.handleMouseClick);
    
    if (this.mouseInterval) {
      clearInterval(this.mouseInterval);
      this.mouseInterval = null;
    }
    
    // Flush any remaining data
    this.flushMouseBuffer();
    
    console.log('Mouse monitoring stopped');
  }

  /**
   * Start device monitoring
   * @param {string} userId - User ID
   * @param {string} token - Authentication token
   */
  startDeviceMonitoring(userId, token) {
    if (this.deviceInterval) return;
    
    this.userId = userId;
    this.token = token;
    this.monitoringActive = true;
    
    // Collect initial device data
    this.collectDeviceData();
    
    // Set up interval to periodically collect and send data
    this.deviceInterval = setInterval(() => {
      this.collectDeviceData();
      this.flushDeviceBuffer();
    }, 30000); // Every 30 seconds
    
    console.log('Device monitoring started');
  }

  /**
   * Collect device data
   */
  collectDeviceData() {
    if (!this.monitoringActive) return;
    
    const deviceData = {
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
      language: navigator.language,
      platform: navigator.platform,
      screenWidth: window.screen.width,
      screenHeight: window.screen.height,
      windowWidth: window.innerWidth,
      windowHeight: window.innerHeight,
      pixelRatio: window.devicePixelRatio,
      timeZoneOffset: new Date().getTimezoneOffset(),
      connection: navigator.connection ? {
        effectiveType: navigator.connection.effectiveType,
        downlink: navigator.connection.downlink,
        rtt: navigator.connection.rtt
      } : null
    };
    
    this.deviceBuffer.push(deviceData);
  }

  /**
   * Send device data to the server
   */
  async flushDeviceBuffer() {
    if (this.deviceBuffer.length === 0) return;
    
    const dataToSend = [...this.deviceBuffer];
    this.deviceBuffer = [];
    
    try {
      await fetch(`${API_BASE_URL}/behavior/device`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`,
        },
        body: JSON.stringify({
          userId: this.userId,
          data: dataToSend
        }),
      });
    } catch (error) {
      console.error('Error sending device data:', error);
    }
  }

  /**
   * Stop device monitoring
   */
  stopDeviceMonitoring() {
    if (this.deviceInterval) {
      clearInterval(this.deviceInterval);
      this.deviceInterval = null;
    }
    
    // Flush any remaining data
    this.flushDeviceBuffer();
    
    console.log('Device monitoring stopped');
  }

  /**
   * Stop all monitoring
   */
  stopAllMonitoring() {
    this.monitoringActive = false;
    this.stopKeystrokeMonitoring();
    this.stopMouseMonitoring();
    this.stopDeviceMonitoring();
    
    console.log('All behavioral monitoring stopped');
  }
}

export const behaviorService = new BehaviorService();