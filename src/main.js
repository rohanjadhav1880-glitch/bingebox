import './style.css';
import defaultLogo from './assets/logo.png';
import {
  createIcons,
  Play,
  Pause,
  Volume2,
  Volume1,
  VolumeX,
  Maximize,
  Minimize,
  SkipBack,
  SkipForward,
  SlidersHorizontal,
  ListVideo,
  Sliders,
  Sun,
  Type,
  Bookmark,
  Keyboard,
  Trash2,
  UploadCloud,
  Plus,
  FileText,
  BookmarkPlus,
  Info,
  Gauge,
  Monitor,
  PictureInPicture,
  Shuffle,
  Repeat,
  Repeat1,
  Video
} from 'lucide';

// ==========================================================================
// STATE MANAGEMENT & ELECTRON BRIDGE
// ==========================================================================
const electronAPI = window.electronAPI || (window.require ? {
  minimize: () => window.require('electron').ipcRenderer.send('window-minimize'),
  maximize: () => window.require('electron').ipcRenderer.send('window-maximize'),
  close: () => window.require('electron').ipcRenderer.send('window-close'),
  openFileDialog: () => window.require('electron').ipcRenderer.invoke('open-file-dialog'),
  selectDirectoryDialog: () => window.require('electron').ipcRenderer.invoke('select-directory-dialog'),
  scanDirectoryPath: (p) => window.require('electron').ipcRenderer.invoke('scan-directory-path', p),
  onGlobalPlayPause: (cb) => {
    window.require('electron').ipcRenderer.on('global-play-pause', cb);
    return () => window.require('electron').ipcRenderer.removeListener('global-play-pause', cb);
  },
  onGlobalNextTrack: (cb) => {
    window.require('electron').ipcRenderer.on('global-next-track', cb);
    return () => window.require('electron').ipcRenderer.removeListener('global-next-track', cb);
  },
  onGlobalPrevTrack: (cb) => {
    window.require('electron').ipcRenderer.on('global-prev-track', cb);
    return () => window.require('electron').ipcRenderer.removeListener('global-prev-track', cb);
  }
} : null);

const ipcRenderer = electronAPI ? {
  send: (channel, ...args) => {
    if (channel === 'window-minimize') electronAPI.minimize();
    else if (channel === 'window-maximize') electronAPI.maximize();
    else if (channel === 'window-close') electronAPI.close();
  },
  invoke: (channel, ...args) => {
    if (channel === 'open-file-dialog') return electronAPI.openFileDialog();
    if (channel === 'select-directory-dialog') return electronAPI.selectDirectoryDialog();
    if (channel === 'scan-directory-path') return electronAPI.scanDirectoryPath(args[0]);
    return Promise.resolve(null);
  },
  on: (channel, cb) => {
    if (channel === 'global-play-pause' && electronAPI.onGlobalPlayPause) return electronAPI.onGlobalPlayPause(cb);
    if (channel === 'global-next-track' && electronAPI.onGlobalNextTrack) return electronAPI.onGlobalNextTrack(cb);
    if (channel === 'global-prev-track' && electronAPI.onGlobalPrevTrack) return electronAPI.onGlobalPrevTrack(cb);
  }
} : null;

const state = {
  playlist: [
    {
      id: 'bunny',
      name: 'Big Buck Bunny (Animation)',
      url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
      source: 'Remote CDN',
      subtitles: []
    },
    {
      id: 'elephants',
      name: 'Elephants Dream (Sci-Fi)',
      url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4',
      source: 'Remote CDN',
      subtitles: []
    },
    {
      id: 'tears',
      name: 'Tears of Steel (VFX Demo)',
      url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4',
      source: 'Remote CDN',
      subtitles: []
    },
    {
      id: 'sintel',
      name: 'Sintel (Fantasy CGI)',
      url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4',
      source: 'Remote CDN',
      subtitles: []
    }
  ],
  currentIndex: 0,
  repeatMode: 'off', // 'off' | 'one' | 'all'
  shuffle: false,
  rebindingAction: null, // Holds action name when waiting for keypress
  keybindings: {}, // Custom shortcut bindings
  scannedFolder: '', // Path to local PC media folder
  libraryFiles: [],  // Scanned media files array
  bookmarks: {}, // Key: videoUrl, Value: Array of { time, title }
  subtitles: {
    cues: [],
    delay: 0.0,
    enabled: false,
    fileName: ''
  },
  controlsTimeout: null,
  abLoop: {
    start: null,
    end: null,
    active: false
  },
  theme: 'obsidian',
  accent: 'violet',
  normalizerEnabled: false,
  transform: {
    zoom: 1.0,
    rotation: 0,
    mirror: false,
    panX: 0,
    panY: 0
  },
  audio: {
    ctx: null,
    source: null,
    filters: [],
    gainNode: null,
    analyserNode: null,
    delayNode: null,
    compressorNode: null,
    vocalFilterNode: null,
    normalizerNode: null,
    normalizerGainNode: null,
    initialized: false
  }
};

// Default Keyboard Shortcuts Configuration Map
const DEFAULT_KEYBINDINGS = {
  playPause: { label: 'Play / Pause', key: ' ', code: 'Space', display: 'Space' },
  mute: { label: 'Mute / Unmute', key: 'm', display: 'M' },
  fullscreen: { label: 'Toggle Fullscreen', key: 'f', display: 'F' },
  pip: { label: 'Picture-in-Picture', key: 'p', display: 'P' },
  subtitles: { label: 'Toggle Subtitles', key: 'c', display: 'C' },
  seekBack: { label: 'Seek Backward 5s', key: 'arrowleft', display: 'Left Arrow' },
  seekFwd: { label: 'Seek Forward 5s', key: 'arrowright', display: 'Right Arrow' },
  seekBack10: { label: 'Seek Backward 10s', key: 'j', display: 'J' },
  seekFwd10: { label: 'Seek Forward 10s', key: 'l', display: 'L' },
  volUp: { label: 'Volume Up', key: 'arrowup', display: 'Up Arrow' },
  volDown: { label: 'Volume Down', key: 'arrowdown', display: 'Down Arrow' },
  next: { label: 'Next Video', key: 'n', display: 'N' },
  prev: { label: 'Previous Video', key: 'n', shift: true, display: 'Shift + N' },
  shuffle: { label: 'Toggle Shuffle', key: 's', display: 'S' },
  repeat: { label: 'Cycle Repeat Mode', key: 'r', display: 'R' },
  abLoop: { label: 'A-B Segment Loop', key: 'a', display: 'A' }
};

// LocalStorage Persistence helper
const loadPersistedData = () => {
  const localPlaylist = localStorage.getItem('bingebox_playlist') || localStorage.getItem('aether_playlist');
  if (localPlaylist) {
    try {
      const parsed = JSON.parse(localPlaylist);
      // Filter out local File URLs as they expire on refresh, keep URL/Remote sources
      state.playlist = parsed.filter(item => !item.url.startsWith('blob:'));
      if (state.playlist.length === 0) {
        // Fallback to default
        state.playlist = [
          {
            id: 'bunny',
            name: 'Big Buck Bunny (Animation)',
            url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
            source: 'Remote CDN'
          },
          {
            id: 'elephants',
            name: 'Elephants Dream (Sci-Fi)',
            url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4',
            source: 'Remote CDN'
          }
        ];
      }
    } catch (e) {
      console.error('Error parsing persisted playlist', e);
    }
  }

  const localBookmarks = localStorage.getItem('bingebox_bookmarks') || localStorage.getItem('aether_bookmarks');
  if (localBookmarks) {
    try {
      state.bookmarks = JSON.parse(localBookmarks);
    } catch (e) {
      console.error('Error parsing persisted bookmarks', e);
    }
  }

  const localKeybindings = localStorage.getItem('bingebox_keybindings') || localStorage.getItem('aether_keybindings');
  if (localKeybindings) {
    try {
      state.keybindings = JSON.parse(localKeybindings);
      if (!state.keybindings.abLoop) {
        state.keybindings.abLoop = JSON.parse(JSON.stringify(DEFAULT_KEYBINDINGS.abLoop));
      }
    } catch (e) {
      console.error('Error parsing persisted keybindings', e);
      state.keybindings = JSON.parse(JSON.stringify(DEFAULT_KEYBINDINGS));
    }
  } else {
    state.keybindings = JSON.parse(JSON.stringify(DEFAULT_KEYBINDINGS));
  }
  const localScannedFolder = localStorage.getItem('bingebox_scanned_folder') || localStorage.getItem('aether_scanned_folder');
  if (localScannedFolder) {
    state.scannedFolder = localScannedFolder;
  }
  const localTheme = localStorage.getItem('bingebox_theme') || localStorage.getItem('aether_theme');
  if (localTheme) {
    state.theme = localTheme;
  } else {
    state.theme = 'obsidian';
  }
  const localAccent = localStorage.getItem('bingebox_accent') || localStorage.getItem('aether_accent');
  if (localAccent) {
    state.accent = localAccent;
  } else {
    state.accent = 'violet';
  }
  const localNormalizer = localStorage.getItem('bingebox_normalizer_enabled') || localStorage.getItem('aether_normalizer_enabled');
  if (localNormalizer) {
    state.normalizerEnabled = localNormalizer === 'true';
  } else {
    state.normalizerEnabled = false;
  }
};

const savePlaylist = () => {
  const serializable = state.playlist.filter(item => !item.url.startsWith('blob:'));
  localStorage.setItem('bingebox_playlist', JSON.stringify(serializable));
};

const saveBookmarks = () => {
  localStorage.setItem('bingebox_bookmarks', JSON.stringify(state.bookmarks));
};

const saveKeybindings = () => {
  localStorage.setItem('bingebox_keybindings', JSON.stringify(state.keybindings));
};

const saveScannedFolder = () => {
  localStorage.setItem('bingebox_scanned_folder', state.scannedFolder);
};

// Video Thumbnail Extractor & Cache
const thumbnailCache = new Map();

const extractVideoThumbnail = (url) => {
  return new Promise((resolve) => {
    const videoEl = document.createElement('video');
    videoEl.src = url;
    videoEl.crossOrigin = 'anonymous';
    videoEl.currentTime = 1; // Seek to 1 second
    videoEl.muted = true;
    videoEl.playsInline = true;
    
    // Safety timeout
    const timeoutId = setTimeout(() => {
      videoEl.src = '';
      videoEl.load();
      resolve(null);
    }, 3000);
    
    videoEl.addEventListener('seeked', () => {
      clearTimeout(timeoutId);
      try {
        const canvas = document.createElement('canvas');
        canvas.width = 160;
        canvas.height = 90;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL('image/jpeg', 0.6);
        resolve(dataUrl);
      } catch (err) {
        console.error('Failed to capture canvas frame', err);
        resolve(null);
      } finally {
        videoEl.src = '';
        videoEl.load();
      }
    });
    
    videoEl.addEventListener('error', () => {
      clearTimeout(timeoutId);
      videoEl.src = '';
      videoEl.load();
      resolve(null);
    });
  });
};

const requestThumbnailElement = (item, index, imgElement) => {
  const url = item.url;
  if (thumbnailCache.has(url)) {
    const thumb = thumbnailCache.get(url);
    imgElement.src = thumb;
    item.thumbnail = thumb;
    return;
  }
  
  extractVideoThumbnail(url).then(thumb => {
    if (thumb) {
      thumbnailCache.set(url, thumb);
      imgElement.src = thumb;
      item.thumbnail = thumb;
      if (index !== null) {
        savePlaylist();
      }
    }
  }).catch(() => {});
};

// Initialize App State
loadPersistedData();

// ==========================================================================
// DOM ELEMENT SELECTORS
// ==========================================================================
const video = document.getElementById('main-video');
const videoContainer = document.getElementById('video-container');
const progressContainer = document.getElementById('seek-bar-container');
const progressBar = document.getElementById('progress-bar');
const bufferBar = document.getElementById('buffer-bar');
const seekTooltip = document.getElementById('seek-tooltip');
const chaptersMarkers = document.getElementById('chapters-markers');

const playBtn = document.getElementById('play-btn');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const shuffleBtn = document.getElementById('shuffle-btn');
const repeatBtn = document.getElementById('repeat-btn');
const muteBtn = document.getElementById('mute-btn');
const volumeSlider = document.getElementById('volume-slider');
const currentTimeEl = document.getElementById('current-time');
const totalDurationEl = document.getElementById('total-duration');

const speedMenuBtn = document.getElementById('speed-menu-btn');
const speedMenu = document.getElementById('speed-menu');
const speedBadge = document.getElementById('speed-badge');
const aspectMenuBtn = document.getElementById('aspect-menu-btn');
const aspectMenu = document.getElementById('aspect-menu');
const videoSettingsBtn = document.getElementById('video-settings-btn');
const subtitlesToggle = document.getElementById('subtitles-toggle');
const pipBtn = document.getElementById('pip-btn');
const fullscreenBtn = document.getElementById('fullscreen-btn');

const centralIndicator = document.getElementById('central-indicator');
const bufferingSpinner = document.getElementById('buffering-spinner');
const subtitleText = document.getElementById('subtitle-text');

// Audio visualizer & ambient
const visualizerCanvas = document.getElementById('audio-visualizer-canvas');
const ambientCanvas = document.getElementById('ambient-glow-canvas');

// Sidebar Tabs & Panels
const tabButtons = document.querySelectorAll('.tab-btn');
const tabPanels = document.querySelectorAll('.tab-panel');

// Sidebar Playlist DOM
const playlistList = document.getElementById('playlist-list');
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const urlInput = document.getElementById('url-input');
const urlSubmitBtn = document.getElementById('url-submit-btn');
const clearPlaylistBtn = document.getElementById('clear-playlist');

// Sidebar Equalizer DOM
const volumeBooster = document.getElementById('volume-booster');
const volumeBoosterVal = document.getElementById('booster-val');
const bassBoost = document.getElementById('bass-boost');
const bassBoostVal = document.getElementById('bass-boost-val');
const eqBandSliders = document.querySelectorAll('.eq-band-range');
const eqPresetButtons = document.querySelectorAll('.preset-btn');
const resetEqBtn = document.getElementById('reset-eq');
const visualizerToggle = document.getElementById('visualizer-toggle');
const visualizerType = document.getElementById('visualizer-type');

// Sidebar Filters DOM
const filterSliders = {
  brightness: document.getElementById('filter-brightness'),
  contrast: document.getElementById('filter-contrast'),
  saturation: document.getElementById('filter-saturation'),
  hue: document.getElementById('filter-hue'),
  blur: document.getElementById('filter-blur'),
  invert: document.getElementById('filter-invert')
};
const filterVals = {
  brightness: document.getElementById('brightness-val'),
  contrast: document.getElementById('contrast-val'),
  saturation: document.getElementById('saturation-val'),
  hue: document.getElementById('hue-val'),
  blur: document.getElementById('blur-val'),
  invert: document.getElementById('invert-val')
};
const resetFiltersBtn = document.getElementById('reset-filters');
const effectPresetButtons = document.querySelectorAll('.effect-btn');

// Sidebar Subtitles DOM
const subFileInput = document.getElementById('sub-file-input');
const activeSubFile = document.getElementById('active-sub-file-name');
const subDelayVal = document.getElementById('sub-delay-val');
const subDelayMinus = document.getElementById('sub-delay-minus');
const subDelayPlus = document.getElementById('sub-delay-plus');
const subDelayReset = document.getElementById('sub-delay-reset');
const resetSubsBtn = document.getElementById('reset-subs');

const subFontSize = document.getElementById('sub-font-size');
const subColor = document.getElementById('sub-color');
const subBgOpacity = document.getElementById('sub-bg-opacity');

// Sidebar Bookmarks DOM
const bookmarkTitleInput = document.getElementById('bookmark-title-input');
const addBookmarkBtn = document.getElementById('add-bookmark-btn');
const bookmarksList = document.getElementById('bookmarks-list');
const bookmarkCountEl = document.getElementById('bookmark-count');
const noBookmarksPlaceholder = document.getElementById('no-bookmarks-placeholder');

// Sidebar Shortcuts DOM
const customShortcutsList = document.getElementById('custom-shortcuts-list');
const resetShortcutsBtn = document.getElementById('reset-shortcuts');

// Sidebar Library DOM
const scanFolderBtn = document.getElementById('scan-folder-btn');
const scannedPathDisplay = document.getElementById('scanned-path-display');
const scannedPathText = document.getElementById('scanned-path-text');
const libraryList = document.getElementById('library-list');
const libraryPlaceholder = document.getElementById('library-placeholder');

// Initial Lucide Icons Render
const refreshIcons = () => {
  createIcons({
    icons: {
      Play,
      Pause,
      Volume2,
      Volume1,
      VolumeX,
      Maximize,
      Minimize,
      SkipBack,
      SkipForward,
      SlidersHorizontal,
      ListVideo,
      Sliders,
      Sun,
      Type,
      Bookmark,
      Keyboard,
      Trash2,
      UploadCloud,
      Plus,
      FileText,
      BookmarkPlus,
      Info,
      Gauge,
      Monitor,
      PictureInPicture,
      Shuffle,
      Repeat,
      Repeat1,
      Video
    }
  });
};

refreshIcons();

// ==========================================================================
// CORE VIDEO PLAYER FUNCTIONS
// ==========================================================================

const formatTime = (timeInSeconds) => {
  if (isNaN(timeInSeconds)) return '00:00';
  const hours = Math.floor(timeInSeconds / 3600);
  const minutes = Math.floor((timeInSeconds % 3600) / 60);
  const seconds = Math.floor(timeInSeconds % 60);

  const formattedMins = minutes.toString().padStart(2, '0');
  const formattedSecs = seconds.toString().padStart(2, '0');

  if (hours > 0) {
    return `${hours}:${formattedMins}:${formattedSecs}`;
  }
  return `${formattedMins}:${formattedSecs}`;
};

// A-B Looper rendering and state helpers
const renderABLoopMarkers = () => {
  document.querySelectorAll('.ab-loop-marker, .ab-loop-region').forEach(el => el.remove());

  if (!video.duration) return;

  const bg = document.querySelector('.progress-bar-bg');
  if (!bg) return;

  if (state.abLoop.start !== null) {
    const startPercent = (state.abLoop.start / video.duration) * 100;
    const startMarker = document.createElement('div');
    startMarker.className = 'ab-loop-marker start';
    startMarker.style.left = `${startPercent}%`;
    bg.appendChild(startMarker);

    if (state.abLoop.end !== null) {
      const endPercent = (state.abLoop.end / video.duration) * 100;
      const endMarker = document.createElement('div');
      endMarker.className = 'ab-loop-marker end';
      endMarker.style.left = `${endPercent}%`;
      bg.appendChild(endMarker);

      const region = document.createElement('div');
      region.className = 'ab-loop-region';
      region.style.left = `${startPercent}%`;
      region.style.width = `${endPercent - startPercent}%`;
      bg.appendChild(region);
    }
  }
};

const updateABLoopUI = () => {
  const btn = document.getElementById('ab-loop-btn');
  const badge = document.getElementById('ab-loop-badge');
  if (!btn || !badge) return;

  if (state.abLoop.start !== null && state.abLoop.end === null) {
    btn.classList.add('active');
    badge.textContent = 'A-?';
    btn.title = 'Set A-B End (B) (A)';
  } else if (state.abLoop.active) {
    btn.classList.add('active');
    badge.textContent = 'A-B';
    btn.title = `Clear A-B Loop (A) [${formatTime(state.abLoop.start)} - ${formatTime(state.abLoop.end)}]`;
  } else {
    btn.classList.remove('active');
    badge.textContent = 'A-B';
    btn.title = 'A-B Segment Loop (A)';
  }

  renderABLoopMarkers();
};

const toggleABLoop = () => {
  if (state.abLoop.start === null) {
    state.abLoop.start = video.currentTime;
    triggerCentralIndicator('repeat-one');
  } else if (state.abLoop.end === null) {
    let t = video.currentTime;
    if (t < state.abLoop.start) {
      state.abLoop.end = state.abLoop.start;
      state.abLoop.start = t;
    } else {
      state.abLoop.end = t;
    }
    if (state.abLoop.end - state.abLoop.start < 0.2) {
      state.abLoop.end += 0.2;
    }
    state.abLoop.active = true;
    video.currentTime = state.abLoop.start;
    triggerCentralIndicator('repeat-all');
  } else {
    state.abLoop.start = null;
    state.abLoop.end = null;
    state.abLoop.active = false;
    triggerCentralIndicator('repeat-off');
  }
  updateABLoopUI();
};

// Load video source
const loadVideo = (index) => {
  if (index < 0 || index >= state.playlist.length) return;
  state.currentIndex = index;
  const item = state.playlist[index];

  // Pause and reset
  video.pause();
  video.src = item.url;
  video.load();

  // Reset Subtitle state for new video
  state.subtitles.cues = [];
  state.subtitles.fileName = '';
  activeSubFile.textContent = 'No subtitle file loaded';
  subtitleText.style.display = 'none';
  subtitlesToggle.classList.remove('active');
  state.subtitles.enabled = false;

  // Reset A-B looper state
  state.abLoop = { start: null, end: null, active: false };
  updateABLoopUI();

  // Reset Zoom & Pan transformations
  resetTransform();

  // Render Playback list details
  renderPlaylistDOM();
  renderBookmarksList();
  renderChaptersOnSeekBar();

  // Reset Buffer and controls progress
  progressBar.style.width = '0%';
  bufferBar.style.width = '0%';
  currentTimeEl.textContent = '00:00';
  totalDurationEl.textContent = '00:00';

  // Apply Current Filters
  applyFilters();
};

const togglePlay = () => {
  if (video.paused || video.ended) {
    // Resume Audio Context on user gesture
    if (state.audio.ctx && state.audio.ctx.state === 'suspended') {
      state.audio.ctx.resume();
    }
    
    // Initialize Web Audio pipeline
    if (!state.audio.initialized) {
      initAudioPipeline();
    }

    video.play();
    triggerCentralIndicator('play');
  } else {
    video.pause();
    triggerCentralIndicator('pause');
  }
};

const updatePlayPauseUI = () => {
  const icon = playBtn.querySelector('i');
  if (video.paused) {
    icon.setAttribute('data-lucide', 'play');
    playBtn.title = 'Play (Space)';
    stopAmbientGlowLoop();
  } else {
    icon.setAttribute('data-lucide', 'pause');
    playBtn.title = 'Pause (Space)';
    
    // Trigger Ambient Glow render loop
    startAmbientGlowLoop();
  }
  refreshIcons();
};

// Central HUD alert animation
const triggerCentralIndicator = (action) => {
  const icon = centralIndicator.querySelector('i');
  centralIndicator.classList.remove('animate');
  void centralIndicator.offsetWidth; // Trigger reflow

  if (action === 'play') {
    icon.setAttribute('data-lucide', 'play');
  } else if (action === 'pause') {
    icon.setAttribute('data-lucide', 'pause');
  } else if (action === 'mute') {
    icon.setAttribute('data-lucide', 'volume-x');
  } else if (action === 'unmute') {
    icon.setAttribute('data-lucide', 'volume-2');
  } else if (action === 'volume-up') {
    icon.setAttribute('data-lucide', 'volume-2');
  } else if (action === 'volume-down') {
    icon.setAttribute('data-lucide', 'volume-1');
  } else if (action === 'fullscreen') {
    icon.setAttribute('data-lucide', 'maximize');
  } else if (action === 'exit-fullscreen') {
    icon.setAttribute('data-lucide', 'minimize');
  } else if (action === 'shuffle-on' || action === 'shuffle-off') {
    icon.setAttribute('data-lucide', 'shuffle');
  } else if (action === 'repeat-all' || action === 'repeat-off') {
    icon.setAttribute('data-lucide', 'repeat');
  } else if (action === 'repeat-one') {
    icon.setAttribute('data-lucide', 'repeat-1');
  } else if (action === 'seek-back') {
    icon.setAttribute('data-lucide', 'skip-back');
  } else if (action === 'seek-fwd') {
    icon.setAttribute('data-lucide', 'skip-forward');
  }
  
  refreshIcons();
  centralIndicator.classList.add('animate');
};

// Skip video buttons
const prevVideo = () => {
  if (state.shuffle && state.playlist.length > 1) {
    let randIdx;
    do {
      randIdx = Math.floor(Math.random() * state.playlist.length);
    } while (randIdx === state.currentIndex);
    loadVideo(randIdx);
    video.play().catch(() => {});
  } else {
    let prevIdx = state.currentIndex - 1;
    if (prevIdx < 0) prevIdx = state.playlist.length - 1;
    loadVideo(prevIdx);
    video.play().catch(() => {});
  }
};

const nextVideo = () => {
  if (state.shuffle && state.playlist.length > 1) {
    let randIdx;
    do {
      randIdx = Math.floor(Math.random() * state.playlist.length);
    } while (randIdx === state.currentIndex);
    loadVideo(randIdx);
    video.play().catch(() => {});
  } else {
    let nextIdx = state.currentIndex + 1;
    if (nextIdx >= state.playlist.length) nextIdx = 0;
    loadVideo(nextIdx);
    video.play().catch(() => {});
  }
};

const toggleShuffle = () => {
  state.shuffle = !state.shuffle;
  shuffleBtn.classList.toggle('active', state.shuffle);
  shuffleBtn.title = state.shuffle ? 'Shuffle Playlist: ON (S)' : 'Shuffle Playlist: OFF (S)';
  triggerCentralIndicator(state.shuffle ? 'shuffle-on' : 'shuffle-off');
};

const toggleRepeatMode = () => {
  const icon = repeatBtn.querySelector('i');
  if (state.repeatMode === 'off') {
    state.repeatMode = 'all';
    repeatBtn.classList.add('active');
    repeatBtn.title = 'Repeat Playlist: ALL (R)';
    icon.setAttribute('data-lucide', 'repeat');
    triggerCentralIndicator('repeat-all');
  } else if (state.repeatMode === 'all') {
    state.repeatMode = 'one';
    repeatBtn.classList.add('active');
    repeatBtn.title = 'Repeat Current: ONE (R)';
    icon.setAttribute('data-lucide', 'repeat-1');
    triggerCentralIndicator('repeat-one');
  } else {
    state.repeatMode = 'off';
    repeatBtn.classList.remove('active');
    repeatBtn.title = 'Repeat Playlist: OFF (R)';
    icon.setAttribute('data-lucide', 'repeat');
    triggerCentralIndicator('repeat-off');
  }
  refreshIcons();
};

// Volume management
const updateVolume = (value) => {
  video.volume = value;
  volumeSlider.value = value;
  video.muted = (value === 0);

  const icon = muteBtn.querySelector('i');
  if (value === 0) {
    icon.setAttribute('data-lucide', 'volume-x');
    muteBtn.title = 'Unmute (M)';
  } else if (value < 0.4) {
    icon.setAttribute('data-lucide', 'volume-1');
    muteBtn.title = 'Mute (M)';
  } else {
    icon.setAttribute('data-lucide', 'volume-2');
    muteBtn.title = 'Mute (M)';
  }
  refreshIcons();
};

const toggleMute = () => {
  if (video.muted) {
    video.muted = false;
    updateVolume(volumeSlider.value > 0 ? volumeSlider.value : 0.7);
    triggerCentralIndicator('unmute');
  } else {
    video.muted = true;
    const icon = muteBtn.querySelector('i');
    icon.setAttribute('data-lucide', 'volume-x');
    refreshIcons();
    triggerCentralIndicator('mute');
  }
};

// Seek Bar Interaction
const seek = (e) => {
  if (!Number.isFinite(video.duration) || video.duration <= 0) return;
  const rect = progressContainer.getBoundingClientRect();
  if (rect.width <= 0) return;
  const clickX = e.clientX - rect.left;
  const percentage = Math.max(0, Math.min(1, clickX / rect.width));
  video.currentTime = percentage * video.duration;
};

// Show Tooltip over seek bar on hover
const handleSeekTooltip = (e) => {
  if (!Number.isFinite(video.duration) || video.duration <= 0) return;
  const rect = progressContainer.getBoundingClientRect();
  if (rect.width <= 0) return;
  const hoverX = e.clientX - rect.left;
  const percentage = Math.max(0, Math.min(1, hoverX / rect.width));
  const hoverTime = percentage * video.duration;
  seekTooltip.textContent = formatTime(hoverTime);
  seekTooltip.style.left = `${hoverX}px`;
};

// Fullscreen
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    videoContainer.requestFullscreen()
      .then(() => {
        videoContainer.classList.add('fullscreen');
        fullscreenBtn.querySelector('i').setAttribute('data-lucide', 'minimize');
        triggerCentralIndicator('fullscreen');
        refreshIcons();
      })
      .catch(err => {
        console.error('Fullscreen request failed', err);
      });
  } else {
    document.exitFullscreen();
  }
};

// Monitor fullscreen events
document.addEventListener('fullscreenchange', () => {
  if (!document.fullscreenElement) {
    videoContainer.classList.remove('fullscreen');
    fullscreenBtn.querySelector('i').setAttribute('data-lucide', 'maximize');
    triggerCentralIndicator('exit-fullscreen');
    refreshIcons();
  }
});

// Picture in Picture
const togglePiP = async () => {
  try {
    if (video !== document.pictureInPictureElement) {
      await video.requestPictureInPicture();
    } else {
      await document.exitPictureInPicture();
    }
  } catch (error) {
    console.error('PiP error', error);
  }
};

// Auto hide custom control bar on mouse idle (useful for fullscreen or clean screen)
const resetControlsTimer = () => {
  videoContainer.classList.remove('controls-hidden');
  clearTimeout(state.controlsTimeout);
  if (!video.paused) {
    state.controlsTimeout = setTimeout(() => {
      videoContainer.classList.add('controls-hidden');
      closeAllDropdowns();
    }, 3000);
  }
};

// Dropdown utility
const closeAllDropdowns = () => {
  speedMenu.classList.remove('active');
  aspectMenu.classList.remove('active');
};

// ==========================================================================
// AMBIENT GLOW LIGHTS (Canvas Frame Rendering)
// ==========================================================================
const ambientCtx = ambientCanvas.getContext('2d', { willReadFrequently: true });
let ambientGlowAnimationId = null;

const stopAmbientGlowLoop = () => {
  if (ambientGlowAnimationId) {
    cancelAnimationFrame(ambientGlowAnimationId);
    ambientGlowAnimationId = null;
  }
};

const startAmbientGlowLoop = () => {
  stopAmbientGlowLoop();
  if (!video.paused && !video.ended) {
    ambientGlowAnimationId = requestAnimationFrame(renderAmbientGlowFrame);
  }
};

const renderAmbientGlowFrame = () => {
  if (video.paused || video.ended) {
    ambientGlowAnimationId = null;
    return;
  }

  // Keep drawing canvas size low for high-performance rendering
  if (ambientCanvas.width !== 64) {
    ambientCanvas.width = 64;
    ambientCanvas.height = 36;
  }

  try {
    ambientCtx.drawImage(video, 0, 0, ambientCanvas.width, ambientCanvas.height);
  } catch (e) {
    // Silently capture frame draw failures on loading state
  }

  ambientGlowAnimationId = requestAnimationFrame(renderAmbientGlowFrame);
};

// ==========================================================================
// AUDIO PROCESSING & VISUALIZER PIPELINE (Web Audio API)
// ==========================================================================
let visualizerAnimationId = null;

const applyNightMode = () => {
  const toggle = document.getElementById('night-mode-toggle');
  if (!toggle) return;

  const isEnabled = toggle.checked;

  if (state.audio.initialized && state.audio.compressorNode && state.audio.vocalFilterNode) {
    const t = state.audio.ctx.currentTime;
    if (isEnabled) {
      state.audio.compressorNode.threshold.setValueAtTime(-35, t);
      state.audio.compressorNode.knee.setValueAtTime(10, t);
      state.audio.compressorNode.ratio.setValueAtTime(6.0, t);
      state.audio.compressorNode.attack.setValueAtTime(0.003, t);
      state.audio.compressorNode.release.setValueAtTime(0.15, t);
      state.audio.vocalFilterNode.gain.setValueAtTime(5.0, t);
    } else {
      state.audio.compressorNode.threshold.setValueAtTime(0, t);
      state.audio.compressorNode.ratio.setValueAtTime(1.0, t);
      state.audio.vocalFilterNode.gain.setValueAtTime(0.0, t);
    }
  }
};

const applyNormalizer = () => {
  const toggle = document.getElementById('normalizer-toggle');
  if (!toggle) return;

  const isEnabled = toggle.checked;
  state.normalizerEnabled = isEnabled;
  localStorage.setItem('bingebox_normalizer_enabled', isEnabled);

  if (state.audio.initialized && state.audio.normalizerNode && state.audio.normalizerGainNode) {
    const t = state.audio.ctx.currentTime;
    if (isEnabled) {
      state.audio.normalizerNode.threshold.setValueAtTime(-24, t);
      state.audio.normalizerNode.knee.setValueAtTime(30, t);
      state.audio.normalizerNode.ratio.setValueAtTime(5.0, t);
      state.audio.normalizerNode.attack.setValueAtTime(0.01, t);
      state.audio.normalizerNode.release.setValueAtTime(0.25, t);
      state.audio.normalizerGainNode.gain.setValueAtTime(2.0, t);
    } else {
      state.audio.normalizerNode.threshold.setValueAtTime(0, t);
      state.audio.normalizerNode.ratio.setValueAtTime(1.0, t);
      state.audio.normalizerGainNode.gain.setValueAtTime(1.0, t);
    }
  }
};

const initAudioPipeline = () => {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    state.audio.ctx = new AudioContext();

    // Create Source from video HTML element
    state.audio.source = state.audio.ctx.createMediaElementSource(video);

    // Create 5 peaking filters for Equalizer bands
    const freqs = [60, 250, 1000, 4000, 16000];
    let currentNode = state.audio.source;

    state.audio.filters = freqs.map((freq, index) => {
      const filter = state.audio.ctx.createBiquadFilter();
      filter.frequency.value = freq;
      filter.Q.value = 1.0;
      
      if (index === 0) {
        filter.type = 'lowshelf';
      } else if (index === freqs.length - 1) {
        filter.type = 'highshelf';
      } else {
        filter.type = 'peaking';
      }

      // Read current EQ sliders values
      filter.gain.value = parseFloat(eqBandSliders[index].value);
      currentNode.connect(filter);
      currentNode = filter;
      return filter;
    });

    // Auto Volume Normalizer Dynamic Compressor & Gain Nodes
    state.audio.normalizerNode = state.audio.ctx.createDynamicsCompressor();
    state.audio.normalizerGainNode = state.audio.ctx.createGain();
    currentNode.connect(state.audio.normalizerNode);
    state.audio.normalizerNode.connect(state.audio.normalizerGainNode);
    currentNode = state.audio.normalizerGainNode;

    // Movie Night Mode Compressor Node
    state.audio.compressorNode = state.audio.ctx.createDynamicsCompressor();
    currentNode.connect(state.audio.compressorNode);
    currentNode = state.audio.compressorNode;

    // Peaking filter for Dialogue Boost (around 1500Hz)
    state.audio.vocalFilterNode = state.audio.ctx.createBiquadFilter();
    state.audio.vocalFilterNode.type = 'peaking';
    state.audio.vocalFilterNode.frequency.value = 1500;
    state.audio.vocalFilterNode.Q.value = 1.2;
    state.audio.vocalFilterNode.gain.value = 0.0;
    currentNode.connect(state.audio.vocalFilterNode);
    currentNode = state.audio.vocalFilterNode;

    // Delay Node for Audio Sync
    state.audio.delayNode = state.audio.ctx.createDelay(2.0); // max delay 2.0s
    state.audio.delayNode.delayTime.value = parseFloat(document.getElementById('audio-sync-slider').value || 0);
    currentNode.connect(state.audio.delayNode);
    currentNode = state.audio.delayNode;

    // Volume booster node (Gain Node)
    state.audio.gainNode = state.audio.ctx.createGain();
    state.audio.gainNode.gain.value = parseFloat(volumeBooster.value);
    currentNode.connect(state.audio.gainNode);
    currentNode = state.audio.gainNode;

    // Analyser Node for drawing dynamic overlays
    state.audio.analyserNode = state.audio.ctx.createAnalyser();
    state.audio.analyserNode.fftSize = 256;
    currentNode.connect(state.audio.analyserNode);

    // Pipe directly to browser speakers (destination)
    state.audio.analyserNode.connect(state.audio.ctx.destination);
    state.audio.initialized = true;

    // Apply night mode if toggled initially
    applyNightMode();

    // Apply volume normalizer if toggled initially
    applyNormalizer();

    // Remove Alert
    document.getElementById('audio-context-init-alert').style.display = 'none';

    // Start Visualizer Loop
    drawVisualizer();
  } catch (error) {
    console.error('Audio initialization failed', error);
  }
};

// Draw Visualizer overlays
const drawVisualizer = () => {
  const visCtx = visualizerCanvas.getContext('2d');
  
  const renderLoop = () => {
    visualizerAnimationId = requestAnimationFrame(renderLoop);

    const isVisEnabled = visualizerToggle.checked;
    if (!isVisEnabled || !state.audio.analyserNode) {
      visCtx.clearRect(0, 0, visualizerCanvas.width, visualizerCanvas.height);
      visualizerCanvas.classList.remove('active');
      return;
    }

    visualizerCanvas.classList.add('active');

    const width = visualizerCanvas.width = visualizerCanvas.clientWidth;
    const height = visualizerCanvas.height = visualizerCanvas.clientHeight;
    const bufferLength = state.audio.analyserNode.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const style = visualizerType.value;

    if (style === 'bars') {
      state.audio.analyserNode.getByteFrequencyData(dataArray);
      visCtx.clearRect(0, 0, width, height);
      
      const barWidth = (width / bufferLength) * 1.5;
      let barHeight;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        barHeight = (dataArray[i] / 255) * height * 0.8;
        
        // Setup beautiful primary-secondary gradient matching cinematic theme
        const grad = visCtx.createLinearGradient(0, height, 0, height - barHeight);
        grad.addColorStop(0, 'rgba(139, 92, 246, 0.05)');
        grad.addColorStop(0.5, 'rgba(139, 92, 246, 0.45)');
        grad.addColorStop(1, 'rgba(59, 130, 246, 0.8)');

        visCtx.fillStyle = grad;
        visCtx.fillRect(x, height - barHeight, barWidth - 2, barHeight);
        x += barWidth;
      }
    } else if (style === 'glowline') {
      state.audio.analyserNode.getByteTimeDomainData(dataArray);
      visCtx.clearRect(0, 0, width, height);

      visCtx.lineWidth = 3;
      
      const grad = visCtx.createLinearGradient(0, 0, width, 0);
      grad.addColorStop(0, '#8b5cf6');
      grad.addColorStop(0.5, '#3b82f6');
      grad.addColorStop(1, '#8b5cf6');
      visCtx.strokeStyle = grad;

      visCtx.shadowBlur = 12;
      visCtx.shadowColor = 'rgba(139, 92, 246, 0.6)';
      visCtx.beginPath();

      const sliceWidth = width / bufferLength;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = (v * height) / 2;

        if (i === 0) {
          visCtx.moveTo(x, y);
        } else {
          visCtx.lineTo(x, y);
        }
        x += sliceWidth;
      }

      visCtx.lineTo(width, height / 2);
      visCtx.stroke();
      visCtx.shadowBlur = 0; // reset shadow
    } else if (style === 'circular') {
      // Circular glowing spectrum ring centered inside screen
      state.audio.analyserNode.getByteFrequencyData(dataArray);
      visCtx.clearRect(0, 0, width, height);

      const cX = width / 2;
      const cY = height / 2;
      const baseR = Math.min(width, height) * 0.22;

      let sum = 0;
      for (let i = 0; i < bufferLength; i++) sum += dataArray[i];
      const avgVolume = sum / bufferLength;
      const pulseRatio = (avgVolume / 255) * 12;

      visCtx.shadowBlur = 15;
      visCtx.shadowColor = 'rgba(139, 92, 246, 0.5)';

      // Outer static ring
      visCtx.beginPath();
      visCtx.arc(cX, cY, baseR + pulseRatio, 0, 2 * Math.PI);
      visCtx.lineWidth = 1.5;
      visCtx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
      visCtx.stroke();

      // Audio reactive halo ring
      const points = 80;
      visCtx.beginPath();
      for (let i = 0; i < points; i++) {
        const angle = (i / points) * 2 * Math.PI;
        const dataIdx = Math.floor((i / points) * bufferLength * 0.65);
        const intensity = dataArray[dataIdx];
        const currentRadius = baseR + pulseRatio + (intensity / 255) * 35;

        const x = cX + Math.cos(angle) * currentRadius;
        const y = cY + Math.sin(angle) * currentRadius;

        if (i === 0) {
          visCtx.moveTo(x, y);
        } else {
          visCtx.lineTo(x, y);
        }
      }
      visCtx.closePath();
      visCtx.lineWidth = 2.5;

      const gradient = visCtx.createRadialGradient(cX, cY, baseR, cX, cY, baseR + 45);
      gradient.addColorStop(0, '#3b82f6');
      gradient.addColorStop(1, '#8b5cf6');
      visCtx.strokeStyle = gradient;
      visCtx.stroke();
      
      visCtx.shadowBlur = 0;
    }
  };

  renderLoop();
};

// Update EQ slider levels
const updateEQBand = (index, value) => {
  const gain = parseFloat(value);
  if (state.audio.filters[index]) {
    state.audio.filters[index].gain.setValueAtTime(gain, state.audio.ctx.currentTime);
  }
  
  // Update UI textual values
  const labels = document.querySelectorAll('.band-val');
  if (labels[index]) {
    labels[index].textContent = (gain > 0 ? '+' : '') + gain + 'dB';
  }
};

// Equalizer Presets config mapping
const eqPresets = {
  flat: [0, 0, 0, 0, 0],
  bass: [8, 4, 0, -2, -4],
  vocal: [-4, -2, 4, 5, 2],
  electronic: [6, 2, -1, 3, 5],
  classical: [4, 2, 1, 2, 4]
};

const applyEQPreset = (presetName) => {
  const gains = eqPresets[presetName];
  if (!gains) return;

  eqBandSliders.forEach((slider, i) => {
    slider.value = gains[i];
    updateEQBand(i, gains[i]);
  });
};

// ==========================================================================
// VIDEO FILTERS MANAGEMENT
// ==========================================================================
const applyFilters = () => {
  const b = filterSliders.brightness.value;
  const c = filterSliders.contrast.value;
  const s = filterSliders.saturation.value;
  const h = filterSliders.hue.value;
  const bl = filterSliders.blur.value;
  const inv = filterSliders.invert.value;

  video.style.filter = `brightness(${b}%) contrast(${c}%) saturate(${s}%) hue-rotate(${h}deg) blur(${bl}px) invert(${inv}%)`;

  filterVals.brightness.textContent = `${b}%`;
  filterVals.contrast.textContent = `${c}%`;
  filterVals.saturation.textContent = `${s}%`;
  filterVals.hue.textContent = `${h}°`;
  filterVals.blur.textContent = `${bl}px`;
  filterVals.invert.textContent = `${inv}%`;
};

const applyQuickEffect = (effect) => {
  // Set values according to preset effects
  const settings = {
    none: [100, 100, 100, 0, 0, 0],
    cinematic: [105, 120, 125, 0, 0, 0],
    noir: [110, 140, 0, 0, 0, 0],
    warm: [95, 90, 85, 20, 0, 0],
    cyberpunk: [100, 115, 160, 140, 0, 0]
  };

  const values = settings[effect];
  if (!values) return;

  let index = 0;
  for (const key in filterSliders) {
    filterSliders[key].value = values[index];
    index++;
  }
  applyFilters();
};

const resetVideoFilters = () => {
  applyQuickEffect('none');
  effectPresetButtons.forEach(btn => btn.classList.remove('active'));
  document.querySelector('[data-effect="none"]').classList.add('active');
  resetTransform();
};

// ==========================================================================
// VIDEO TRANSFORMATIONS & ZOOM (Rotation, Mirroring, Zoom, Offset Pan)
// ==========================================================================
function applyTransform() {
  const zoom = state.transform.zoom;
  const rotation = state.transform.rotation;
  const mirror = state.transform.mirror ? -1 : 1;
  const panX = state.transform.panX;
  const panY = state.transform.panY;

  video.style.transform = `translate(${panX}px, ${panY}px) scale(${zoom}) rotate(${rotation}deg) scaleX(${mirror})`;
}

function updateTransformUI() {
  const zoomValEl = document.getElementById('zoom-val');
  const panXValEl = document.getElementById('pan-x-val');
  const panYValEl = document.getElementById('pan-y-val');
  const mirrorBtn = document.getElementById('transform-mirror-btn');

  if (zoomValEl) zoomValEl.textContent = `${state.transform.zoom.toFixed(1)}x`;
  if (panXValEl) panXValEl.textContent = `${state.transform.panX}px`;
  if (panYValEl) panYValEl.textContent = `${state.transform.panY}px`;
  
  if (mirrorBtn) {
    mirrorBtn.classList.toggle('active', state.transform.mirror);
  }

  document.querySelectorAll('.transform-rot-btn').forEach(btn => {
    const rot = parseInt(btn.getAttribute('data-rot'));
    btn.classList.toggle('active', rot === state.transform.rotation);
  });

  applyTransform();
}

function resetTransform() {
  state.transform = {
    zoom: 1.0,
    rotation: 0,
    mirror: false,
    panX: 0,
    panY: 0
  };

  const zoomInput = document.getElementById('transform-zoom');
  const panXInput = document.getElementById('transform-pan-x');
  const panYInput = document.getElementById('transform-pan-y');

  if (zoomInput) zoomInput.value = 1.0;
  if (panXInput) panXInput.value = 0;
  if (panYInput) panYInput.value = 0;

  updateTransformUI();
}

// ==========================================================================
// SUBTITLES MANAGEMENT (.vtt & .srt parser)
// ==========================================================================

const parseSRT = (text) => {
  const toSeconds = (timeStr) => {
    const cleanTime = timeStr.trim().replace(',', '.');
    const parts = cleanTime.split(':');
    const hrs = parseFloat(parts[0]);
    const mins = parseFloat(parts[1]);
    const secs = parseFloat(parts[2]);
    return hrs * 3600 + mins * 60 + secs;
  };

  const lines = text.split(/\r?\n/);
  const cues = [];
  let currentCue = null;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) {
      if (currentCue) {
        cues.push(currentCue);
        currentCue = null;
      }
      continue;
    }

    const timeMatch = line.match(/([\d:.,]+)\s*-->\s*([\d:.,]+)/);
    if (timeMatch) {
      currentCue = {
        start: toSeconds(timeMatch[1]),
        end: toSeconds(timeMatch[2]),
        text: ''
      };
    } else if (currentCue) {
      currentCue.text = currentCue.text ? currentCue.text + '\n' + line : line;
    }
  }
  if (currentCue) cues.push(currentCue);
  return cues;
};

const parseWebVTT = (text) => {
  const toSeconds = (timeStr) => {
    const parts = timeStr.trim().split(':');
    let hrs = 0;
    let mins = 0;
    let secs = 0;
    
    if (parts.length === 3) {
      hrs = parseFloat(parts[0]);
      mins = parseFloat(parts[1]);
      secs = parseFloat(parts[2]);
    } else {
      mins = parseFloat(parts[0]);
      secs = parseFloat(parts[1]);
    }
    return hrs * 3600 + mins * 60 + secs;
  };

  const lines = text.trim().split(/\r?\n/);
  const cues = [];
  let currentCue = null;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) {
      if (currentCue) {
        cues.push(currentCue);
        currentCue = null;
      }
      continue;
    }
    if (line === 'WEBVTT') continue;

    const timeMatch = line.match(/([\d:.]+)\s*-->\s*([\d:.]+)/);
    if (timeMatch) {
      currentCue = {
        start: toSeconds(timeMatch[1]),
        end: toSeconds(timeMatch[2]),
        text: ''
      };
    } else if (currentCue) {
      currentCue.text = currentCue.text ? currentCue.text + '\n' + line : line;
    }
  }
  if (currentCue) cues.push(currentCue);
  return cues;
};

// Check for active subtitle text on time update
const updateSubtitlesRendering = () => {
  if (!state.subtitles.enabled || state.subtitles.cues.length === 0) {
    subtitleText.style.display = 'none';
    return;
  }

  const adjustedTime = video.currentTime + state.subtitles.delay;
  const currentCue = state.subtitles.cues.find(
    cue => adjustedTime >= cue.start && adjustedTime <= cue.end
  );

  if (currentCue) {
    subtitleText.replaceChildren();
    const lines = (currentCue.text || '').split('\n');
    lines.forEach((line, idx) => {
      if (idx > 0) subtitleText.appendChild(document.createElement('br'));
      subtitleText.appendChild(document.createTextNode(line));
    });
    subtitleText.style.display = 'block';
  } else {
    subtitleText.style.display = 'none';
  }
};

const handleSubtitleUpload = (file) => {
  const reader = new FileReader();
  state.subtitles.fileName = file.name;
  activeSubFile.textContent = file.name;

  reader.onload = (e) => {
    const fileContent = e.target.result;
    const isSrt = file.name.toLowerCase().endsWith('.srt');
    console.log("Loaded subtitle file:", file.name, "Is SRT:", isSrt);
    if (isSrt) {
      state.subtitles.cues = parseSRT(fileContent);
    } else {
      state.subtitles.cues = parseWebVTT(fileContent);
    }
    console.log("Parsed cues count:", state.subtitles.cues.length);
    if (state.subtitles.cues.length > 0) {
      console.log("First cue example:", state.subtitles.cues[0]);
    }

    state.subtitles.enabled = true;
    subtitlesToggle.classList.add('active');
    triggerCentralIndicator('unmute'); // Visual signifier subtitles are loaded
  };

  reader.readAsText(file);
};

// Update subtitle style preferences
const applySubtitleStyles = () => {
  subtitleText.style.fontSize = subFontSize.value;
  subtitleText.style.color = subColor.value;
  subtitleText.style.backgroundColor = subBgOpacity.value;
};

// ==========================================================================
// PLAYLIST MANAGER DOM RENDERING & LIBRARY LOADING
// ==========================================================================

const renderPlaylistDOM = () => {
  playlistList.innerHTML = '';
  state.playlist.forEach((item, index) => {
    const isActive = index === state.currentIndex;
    
    const li = document.createElement('li');
    li.className = `playlist-item ${isActive ? 'active' : ''}`;
    li.setAttribute('data-index', index);

    li.innerHTML = `
      <div class="playlist-item-info">
        <div class="playlist-thumbnail-container">
          <img class="playlist-thumbnail" id="playlist-thumb-${index}" src="${defaultLogo}" alt="${item.name}">
          <div class="playlist-thumbnail-overlay">
            <i data-lucide="${isActive && !video.paused ? 'pause' : 'play'}"></i>
          </div>
        </div>
        <div class="playlist-item-details">
          <span class="playlist-item-name">${item.name}</span>
          <span class="playlist-item-source">${item.source}</span>
        </div>
      </div>
      <button class="playlist-item-remove" title="Remove video">
        <i data-lucide="trash-2"></i>
      </button>
    `;

    const imgEl = li.querySelector(`#playlist-thumb-${index}`);
    if (item.thumbnail) {
      imgEl.src = item.thumbnail;
      thumbnailCache.set(item.url, item.thumbnail);
    } else {
      requestThumbnailElement(item, index, imgEl);
    }

    // Click on item loads video
    li.querySelector('.playlist-item-info').addEventListener('click', () => {
      if (isActive) {
        togglePlay();
      } else {
        loadVideo(index);
        video.play().catch(() => {});
      }
    });

    // Remove from playlist click
    li.querySelector('.playlist-item-remove').addEventListener('click', (e) => {
      e.stopPropagation();
      removePlaylistVideo(index);
    });

    playlistList.appendChild(li);
  });
  
  refreshIcons();
};

const addPlaylistVideo = (name, url, source = 'URL Source') => {
  state.playlist.push({
    id: 'custom-' + Date.now(),
    name: name,
    url: url,
    source: source
  });
  savePlaylist();
  renderPlaylistDOM();

  // If first video added, load it
  if (state.playlist.length === 1) {
    loadVideo(0);
  }
};

const removePlaylistVideo = (index) => {
  const isActive = index === state.currentIndex;
  state.playlist.splice(index, 1);
  savePlaylist();
  
  if (state.playlist.length === 0) {
    video.src = '';
    video.pause();
    currentTimeEl.textContent = '00:00';
    totalDurationEl.textContent = '00:00';
    progressBar.style.width = '0%';
    bufferBar.style.width = '0%';
  } else if (isActive) {
    // Current loaded video was deleted, load another one
    const newIdx = Math.max(0, index - 1);
    loadVideo(newIdx);
  } else if (index < state.currentIndex) {
    // Shrink index down to remain on current video
    state.currentIndex--;
  }

  renderPlaylistDOM();
};

// Drag & drop file uploads
const SUPPORTED_MEDIA_EXTS = ['.mp4', '.mkv', '.webm', '.ogg', '.avi', '.mov', '.flv', '.ts', '.m4v', '.wmv', '.mp3', '.wav', '.aac', '.flac', '.m4a'];

const handleFilesUpload = (files) => {
  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    const nameLower = (file.name || '').toLowerCase();
    const isSupported = (file.type && (file.type.startsWith('video/') || file.type.startsWith('audio/'))) ||
                        SUPPORTED_MEDIA_EXTS.some(ext => nameLower.endsWith(ext));
    if (isSupported) {
      let fileUrl;
      if (file.path) {
        const cleanPath = file.path.replace(/\\/g, '/');
        fileUrl = cleanPath.startsWith('/') ? `file://${cleanPath}` : `file:///${cleanPath}`;
      } else {
        fileUrl = URL.createObjectURL(file);
      }
      addPlaylistVideo(file.name, fileUrl, file.path ? 'PC Local File' : 'Local File');
    }
  }
};

// ==========================================================================
// LOCAL DIRECTORY LIBRARY SCANNER FUNCTIONS
// ==========================================================================

const formatBytes = (bytes, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

const renderLibraryDOM = () => {
  libraryList.innerHTML = '';

  if (!state.scannedFolder || state.libraryFiles.length === 0) {
    libraryList.appendChild(libraryPlaceholder);
    scannedPathDisplay.style.display = 'none';
    return;
  }

  // Display scanned folder path
  scannedPathDisplay.style.display = 'flex';
  scannedPathText.textContent = state.scannedFolder;

  state.libraryFiles.forEach(file => {
    // Format local system filepath to file:// URL scheme
    const cleanPath = file.path.replace(/\\/g, '/');
    const fileUrl = cleanPath.startsWith('/') ? `file://${cleanPath}` : `file:///${cleanPath}`;
    
    const inPlaylist = state.playlist.some(item => item.url === fileUrl);
    const isPlaying = inPlaylist && state.playlist[state.currentIndex]?.url === fileUrl && !video.paused;

    const li = document.createElement('li');
    li.className = `playlist-item ${isPlaying ? 'active' : ''}`;
    
    const safeId = cleanPath.replace(/[^a-zA-Z0-9]/g, '_');
    li.innerHTML = `
      <div class="playlist-item-info" style="flex: 1; overflow: hidden; padding-right: 8px;">
        <div class="playlist-thumbnail-container" style="margin-right: 0.5rem;">
          <img class="playlist-thumbnail" id="library-thumb-${safeId}" src="${defaultLogo}" alt="${file.name}">
          <div class="playlist-thumbnail-overlay">
            <i data-lucide="${isPlaying ? 'pause' : 'play'}"></i>
          </div>
        </div>
        <div class="playlist-item-details" style="overflow: hidden; width: 100%;">
          <span class="playlist-item-name" title="${file.name}" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block;">${file.name}</span>
          <span class="playlist-item-source" style="font-size: 0.7rem; color: var(--text-muted);">${formatBytes(file.size)}</span>
        </div>
      </div>
      <div class="library-item-actions" style="display: flex; gap: 0.25rem; align-items: center; flex-shrink: 0;">
        <button class="panel-btn-action play-lib-item" title="${isPlaying ? 'Pause' : 'Play Now'}" style="color: var(--secondary); background: rgba(59, 130, 246, 0.08); padding: 5px; border-radius: 6px; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;">
          <i data-lucide="${isPlaying ? 'pause' : 'play'}" style="width: 14px; height: 14px;"></i>
        </button>
        <button class="panel-btn-action add-lib-item" title="Add to Playlist" style="color: var(--primary); background: rgba(139, 92, 246, 0.08); padding: 5px; border-radius: 6px; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; ${inPlaylist ? 'opacity: 0.25; cursor: not-allowed;' : ''}" ${inPlaylist ? 'disabled' : ''}>
          <i data-lucide="plus" style="width: 14px; height: 14px;"></i>
        </button>
      </div>
    `;

    const imgEl = li.querySelector(`#library-thumb-${safeId}`);
    requestThumbnailElement({ url: fileUrl }, null, imgEl);

    // Click play
    li.querySelector('.play-lib-item').addEventListener('click', (e) => {
      e.stopPropagation();
      if (isPlaying) {
        togglePlay();
      } else {
        if (!inPlaylist) {
          addPlaylistVideo(file.name, fileUrl, 'Local Library');
          loadVideo(state.playlist.length - 1);
        } else {
          const plIdx = state.playlist.findIndex(item => item.url === fileUrl);
          if (plIdx !== -1) loadVideo(plIdx);
        }
        video.play().catch(() => {});
      }
    });

    // Click add to playlist
    li.querySelector('.add-lib-item').addEventListener('click', (e) => {
      e.stopPropagation();
      if (!inPlaylist) {
        addPlaylistVideo(file.name, fileUrl, 'Local Library');
        renderLibraryDOM(); // Refresh buttons
      }
    });

    libraryList.appendChild(li);
  });

  refreshIcons();
};

const scanFolderAction = async () => {
  if (!ipcRenderer) {
    alert('Local Library scanning is only available in the Desktop PC application!');
    return;
  }
  
  try {
    const result = await ipcRenderer.invoke('select-directory-dialog');
    if (result) {
      state.scannedFolder = result.dirPath;
      state.libraryFiles = result.files;
      saveScannedFolder();
      renderLibraryDOM();
    }
  } catch (err) {
    console.error('Error scanning folder', err);
  }
};

const autoScanSavedFolder = async () => {
  if (!ipcRenderer || !state.scannedFolder) return;
  try {
    const result = await ipcRenderer.invoke('scan-directory-path', state.scannedFolder);
    if (result) {
      state.libraryFiles = result.files;
      renderLibraryDOM();
    }
  } catch (err) {
    console.error('Error auto-scanning saved folder', err);
  }
};

// ==========================================================================
// BOOKMARKS & NOTES HANDLERS
// ==========================================================================

const getBookmarksForCurrent = () => {
  const currentVideo = state.playlist[state.currentIndex];
  if (!currentVideo) return [];
  // Key by video URL
  if (!state.bookmarks[currentVideo.url]) {
    state.bookmarks[currentVideo.url] = [];
  }
  return state.bookmarks[currentVideo.url];
};

const renderBookmarksList = () => {
  const bList = getBookmarksForCurrent();
  
  // Update badge count
  bookmarkCountEl.textContent = `${bList.length} bookmark${bList.length !== 1 ? 's' : ''}`;

  // Reset inner html
  bookmarksList.innerHTML = '';

  if (bList.length === 0) {
    bookmarksList.appendChild(noBookmarksPlaceholder);
    return;
  }

  // Sort bookmarks chronologically
  const sorted = [...bList].sort((a, b) => a.time - b.time);

  sorted.forEach((item, index) => {
    const li = document.createElement('li');
    li.className = 'bookmark-item';
    li.innerHTML = `
      <div class="bookmark-meta">
        <span class="bookmark-timestamp" title="Seek to ${formatTime(item.time)}">${formatTime(item.time)}</span>
        <button class="bookmark-delete" title="Delete bookmark">
          <i data-lucide="trash-2"></i>
        </button>
      </div>
      <span class="bookmark-text">${item.title}</span>
    `;

    // Time Click Seeks
    li.querySelector('.bookmark-timestamp').addEventListener('click', () => {
      video.currentTime = item.time;
      if (video.paused) {
        video.play().catch(() => {});
      }
    });

    // Delete bookmark click
    li.querySelector('.bookmark-delete').addEventListener('click', () => {
      const list = getBookmarksForCurrent();
      // Remove specific bookmark matching time and title
      const actualIdx = list.findIndex(b => b.time === item.time && b.title === item.title);
      if (actualIdx !== -1) {
        list.splice(actualIdx, 1);
        saveBookmarks();
        renderBookmarksList();
        renderChaptersOnSeekBar();
      }
    });

    bookmarksList.appendChild(li);
  });

  refreshIcons();
};

const addBookmark = () => {
  const text = bookmarkTitleInput.value.trim();
  if (!text) return;

  const currentVideo = state.playlist[state.currentIndex];
  if (!currentVideo) return;

  const list = getBookmarksForCurrent();
  const time = video.currentTime;

  list.push({
    time: time,
    title: text
  });

  saveBookmarks();
  bookmarkTitleInput.value = '';
  renderBookmarksList();
  renderChaptersOnSeekBar();
};

// Render small visual markers on seek bar
const renderChaptersOnSeekBar = () => {
  chaptersMarkers.innerHTML = '';
  if (!video.duration) return;

  const list = getBookmarksForCurrent();
  list.forEach(b => {
    const percentage = (b.time / video.duration) * 100;
    const dot = document.createElement('div');
    dot.className = 'chapter-marker-dot';
    dot.style.left = `${percentage}%`;
    dot.title = `${formatTime(b.time)}: ${b.title}`;
    chaptersMarkers.appendChild(dot);
  });
};

// ==========================================================================
// BROWSER & USER INTERACTION EVENT BINDINGS
// ==========================================================================

// Playback Video Engine Event Listeners
video.addEventListener('play', updatePlayPauseUI);
video.addEventListener('pause', updatePlayPauseUI);

video.addEventListener('timeupdate', () => {
  // A-B Looper segment checking
  if (state.abLoop.active && state.abLoop.start !== null && state.abLoop.end !== null) {
    if (video.currentTime >= state.abLoop.end || video.currentTime < state.abLoop.start) {
      video.currentTime = state.abLoop.start;
    }
  }

  // Seek bar updates
  if (video.duration) {
    const percentage = (video.currentTime / video.duration) * 100;
    progressBar.style.width = `${percentage}%`;
    currentTimeEl.textContent = formatTime(video.currentTime);
  }

  // Captions overlays
  updateSubtitlesRendering();
});

video.addEventListener('progress', () => {
  // Buffered track update
  if (video.duration && video.buffered.length > 0) {
    const bufferedEnd = video.buffered.end(video.buffered.length - 1);
    const bufferedPercent = (bufferedEnd / video.duration) * 100;
    bufferBar.style.width = `${bufferedPercent}%`;
  }
});

video.addEventListener('loadedmetadata', () => {
  totalDurationEl.textContent = formatTime(video.duration);
  renderChaptersOnSeekBar();
  renderABLoopMarkers();
});

video.addEventListener('waiting', () => {
  bufferingSpinner.classList.add('active');
});

video.addEventListener('playing', () => {
  bufferingSpinner.classList.remove('active');
  
  // Extract thumbnail 1s after playing, if not already captured
  setTimeout(() => {
    const currentVideo = state.playlist[state.currentIndex];
    if (currentVideo && !currentVideo.thumbnail) {
      try {
        const canvas = document.createElement('canvas');
        canvas.width = 160;
        canvas.height = 90;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL('image/jpeg', 0.6);
        currentVideo.thumbnail = dataUrl;
        thumbnailCache.set(currentVideo.url, dataUrl);
        savePlaylist();
        renderPlaylistDOM();
      } catch (e) {
        console.warn('Could not capture frame from playing video:', e);
      }
    }
  }, 1000);
});

video.addEventListener('ended', () => {
  if (state.repeatMode === 'one') {
    video.currentTime = 0;
    video.play().catch(() => {});
  } else if (state.shuffle && state.playlist.length > 1) {
    let randIdx;
    do {
      randIdx = Math.floor(Math.random() * state.playlist.length);
    } while (randIdx === state.currentIndex);
    loadVideo(randIdx);
    video.play().catch(() => {});
  } else {
    // Standard sequence advance
    if (state.currentIndex === state.playlist.length - 1) {
      if (state.repeatMode === 'all') {
        loadVideo(0);
        video.play().catch(() => {});
      } else {
        video.pause();
      }
    } else {
      nextVideo();
    }
  }
});

// Control bar interactions
playBtn.addEventListener('click', togglePlay);
prevBtn.addEventListener('click', prevVideo);
nextBtn.addEventListener('click', nextVideo);
shuffleBtn.addEventListener('click', toggleShuffle);
repeatBtn.addEventListener('click', toggleRepeatMode);
muteBtn.addEventListener('click', toggleMute);
fullscreenBtn.addEventListener('click', toggleFullscreen);
pipBtn.addEventListener('click', togglePiP);

volumeSlider.addEventListener('input', (e) => {
  updateVolume(parseFloat(e.target.value));
});

progressContainer.addEventListener('click', seek);
progressContainer.addEventListener('mousemove', handleSeekTooltip);

// Handle speed control
speedMenuBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  closeAllDropdowns();
  speedMenu.classList.toggle('active');
});

speedMenu.querySelectorAll('button').forEach(btn => {
  btn.addEventListener('click', () => {
    const rate = parseFloat(btn.getAttribute('data-speed'));
    video.playbackRate = rate;
    
    speedBadge.textContent = rate === 1 ? '1x' : `${rate}x`;
    
    speedMenu.querySelectorAll('button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    closeAllDropdowns();
  });
});

// Handle Aspect Ratio Controls
aspectMenuBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  closeAllDropdowns();
  aspectMenu.classList.toggle('active');
});

aspectMenu.querySelectorAll('button').forEach(btn => {
  btn.addEventListener('click', () => {
    const ratio = btn.getAttribute('data-aspect');
    
    // Reset classes
    videoContainer.classList.remove('aspect-fit', 'aspect-stretch', 'aspect-16-9', 'aspect-4-3', 'aspect-21-9');
    videoContainer.classList.add(`aspect-${ratio}`);

    aspectMenu.querySelectorAll('button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    closeAllDropdowns();
  });
});

// Settings button jumps to filters tab
videoSettingsBtn.addEventListener('click', () => {
  // Switch to Filters panel
  document.querySelector('[data-tab="filters"]').click();
});

// Subtitle bar toggle
subtitlesToggle.addEventListener('click', () => {
  state.subtitles.enabled = !state.subtitles.enabled;
  subtitlesToggle.classList.toggle('active');
  if (!state.subtitles.enabled) {
    subtitleText.style.display = 'none';
  }
});

// Document click closes dropdowns & releases focus from buttons to prevent space-key retriggering issues
document.addEventListener('click', (e) => {
  closeAllDropdowns();
  const btn = e.target.closest('button');
  if (btn) {
    btn.blur();
  }
});

// Hide Control Bar on cursor idle
videoContainer.addEventListener('mousemove', resetControlsTimer);
videoContainer.addEventListener('mouseleave', () => {
  if (!video.paused) {
    videoContainer.classList.add('controls-hidden');
    closeAllDropdowns();
  }
});

// Sidebar panel tabs toggling
tabButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    const targetTab = btn.getAttribute('data-tab');

    tabButtons.forEach(b => b.classList.remove('active'));
    tabPanels.forEach(p => p.classList.remove('active'));

    btn.classList.add('active');
    document.getElementById(`panel-${targetTab}`).classList.add('active');
  });
});

// Playlist Panel Interactions
clearPlaylistBtn.addEventListener('click', () => {
  state.playlist = [];
  savePlaylist();
  renderPlaylistDOM();
  video.src = '';
  video.pause();
  currentTimeEl.textContent = '00:00';
  totalDurationEl.textContent = '00:00';
  progressBar.style.width = '0%';
  bufferBar.style.width = '0%';
});

// Drag and drop events
dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('dragover');
  if (e.dataTransfer.files.length > 0) {
    handleFilesUpload(e.dataTransfer.files);
  }
});

fileInput.addEventListener('change', (e) => {
  if (e.target.files.length > 0) {
    handleFilesUpload(e.target.files);
  }
});

// URL input load
urlSubmitBtn.addEventListener('click', () => {
  const url = urlInput.value.trim();
  if (url) {
    // Generate name based on URL extension
    const urlFilename = url.substring(url.lastIndexOf('/') + 1) || 'Stream Link';
    addPlaylistVideo(urlFilename, url, 'URL Link');
    urlInput.value = '';
  }
});

urlInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    urlSubmitBtn.click();
  }
});

// Equalizer sliders interactions
volumeBooster.addEventListener('input', (e) => {
  const gain = parseFloat(e.target.value);
  volumeBoosterVal.textContent = `${Math.round(gain * 100)}%`;
  
  if (state.audio.gainNode) {
    state.audio.gainNode.gain.setValueAtTime(gain, state.audio.ctx.currentTime);
  }
});

bassBoost.addEventListener('input', (e) => {
  const boostVal = parseFloat(e.target.value);
  bassBoostVal.textContent = `${boostVal} dB`;
  
  // Bass is generally 60Hz (filter 0) and 250Hz (filter 1)
  if (state.audio.filters[0]) {
    // Amplify lower frequencies
    state.audio.filters[0].gain.value = parseFloat(eqBandSliders[0].value) + boostVal;
  }
});

eqBandSliders.forEach((slider, index) => {
  slider.addEventListener('input', (e) => {
    updateEQBand(index, e.target.value);
  });
});

eqPresetButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    eqPresetButtons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const preset = btn.getAttribute('data-preset');
    applyEQPreset(preset);
  });
});

resetEqBtn.addEventListener('click', () => {
  applyEQPreset('flat');
  eqPresetButtons.forEach(b => b.classList.remove('active'));
  document.querySelector('[data-preset="flat"]').classList.add('active');
  volumeBooster.value = 1;
  volumeBoosterVal.textContent = '100%';
  if (state.audio.gainNode) {
    state.audio.gainNode.gain.setValueAtTime(1.0, state.audio.ctx.currentTime);
  }
  bassBoost.value = 0;
  bassBoostVal.textContent = '0 dB';

  // Reset Audio Sync Delay
  if (audioSyncSlider) {
    audioSyncSlider.value = 0;
    audioSyncVal.textContent = '0 ms';
    if (state.audio.initialized && state.audio.delayNode) {
      state.audio.delayNode.delayTime.setValueAtTime(0, state.audio.ctx.currentTime);
    }
  }

  // Reset Movie Night Mode
  if (nightModeToggle) {
    nightModeToggle.checked = false;
    applyNightMode();
  }

  // Reset Volume Normalizer
  if (normalizerToggle) {
    normalizerToggle.checked = false;
    applyNormalizer();
  }
});

// A-B Looper UI Hookup
const abLoopBtn = document.getElementById('ab-loop-btn');
if (abLoopBtn) {
  abLoopBtn.addEventListener('click', () => {
    toggleABLoop();
  });
}

// Window resize updates looper markers positioning
window.addEventListener('resize', renderABLoopMarkers);

// Theme Switching Logic
const applyTheme = (themeName) => {
  document.body.classList.remove('theme-cyberpunk', 'theme-frost', 'theme-light');
  if (themeName !== 'obsidian') {
    document.body.classList.add(`theme-${themeName}`);
  }
  state.theme = themeName;
  localStorage.setItem('bingebox_theme', themeName);

  document.querySelectorAll('.theme-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-theme') === themeName);
  });
};

document.querySelectorAll('.theme-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const themeName = btn.getAttribute('data-theme');
    applyTheme(themeName);
  });
});

// Accent Colors Customizations Mapping
const accentColorMap = {
  violet: { primary: '263, 90%, 66%', secondary: '217, 91%, 60%' },
  cyan: { primary: '188, 90%, 50%', secondary: '200, 95%, 45%' },
  emerald: { primary: '160, 84%, 39%', secondary: '180, 70%, 40%' },
  rose: { primary: '350, 89%, 60%', secondary: '320, 80%, 55%' },
  amber: { primary: '38, 92%, 50%', secondary: '20, 90%, 55%' }
};

const applyAccentColor = (accentName) => {
  const mapping = accentColorMap[accentName];
  if (!mapping) return;

  document.documentElement.style.setProperty('--primary-hsl', mapping.primary);
  document.documentElement.style.setProperty('--secondary-hsl', mapping.secondary);

  state.accent = accentName;
  localStorage.setItem('bingebox_accent', accentName);

  document.querySelectorAll('.accent-color-chip').forEach(chip => {
    const isActive = chip.getAttribute('data-accent') === accentName;
    chip.classList.toggle('active', isActive);
    chip.style.borderColor = isActive ? '#ffffff' : 'transparent';
  });
};

document.querySelectorAll('.accent-color-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    const accentName = chip.getAttribute('data-accent');
    applyAccentColor(accentName);
  });
});

// Night Mode Toggle Interaction
const nightModeToggle = document.getElementById('night-mode-toggle');
if (nightModeToggle) {
  nightModeToggle.addEventListener('change', applyNightMode);
}

// Normalizer Toggle Interaction
const normalizerToggle = document.getElementById('normalizer-toggle');
if (normalizerToggle) {
  normalizerToggle.addEventListener('change', applyNormalizer);
}

// Audio Sync Slider Interaction
const audioSyncSlider = document.getElementById('audio-sync-slider');
const audioSyncVal = document.getElementById('audio-sync-val');

// Filters Sliders Interactions
for (const key in filterSliders) {
  filterSliders[key].addEventListener('input', applyFilters);
}

effectPresetButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    effectPresetButtons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const effect = btn.getAttribute('data-effect');
    applyQuickEffect(effect);
  });
});

resetFiltersBtn.addEventListener('click', resetVideoFilters);

// Video Transformations Event Listeners
const transformZoomInput = document.getElementById('transform-zoom');
if (transformZoomInput) {
  transformZoomInput.addEventListener('input', (e) => {
    state.transform.zoom = parseFloat(e.target.value);
    updateTransformUI();
  });
}

const transformPanXInput = document.getElementById('transform-pan-x');
if (transformPanXInput) {
  transformPanXInput.addEventListener('input', (e) => {
    state.transform.panX = parseInt(e.target.value);
    updateTransformUI();
  });
}

const transformPanYInput = document.getElementById('transform-pan-y');
if (transformPanYInput) {
  transformPanYInput.addEventListener('input', (e) => {
    state.transform.panY = parseInt(e.target.value);
    updateTransformUI();
  });
}

const transformMirrorBtn = document.getElementById('transform-mirror-btn');
if (transformMirrorBtn) {
  transformMirrorBtn.addEventListener('click', () => {
    state.transform.mirror = !state.transform.mirror;
    updateTransformUI();
  });
}

document.querySelectorAll('.transform-rot-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    state.transform.rotation = parseInt(btn.getAttribute('data-rot'));
    updateTransformUI();
  });
});

const resetTransformBtn = document.getElementById('reset-transform');
if (resetTransformBtn) {
  resetTransformBtn.addEventListener('click', () => {
    resetTransform();
  });
}

// Subtitles interactions
subFileInput.addEventListener('change', (e) => {
  if (e.target.files.length > 0) {
    handleSubtitleUpload(e.target.files[0]);
  }
});

// Sync delays buttons
subDelayMinus.addEventListener('click', () => {
  state.subtitles.delay -= 0.5;
  subDelayVal.textContent = `${state.subtitles.delay.toFixed(1)}s`;
});

subDelayPlus.addEventListener('click', () => {
  state.subtitles.delay += 0.5;
  subDelayVal.textContent = `${state.subtitles.delay.toFixed(1)}s`;
});

subDelayReset.addEventListener('click', () => {
  state.subtitles.delay = 0.0;
  subDelayVal.textContent = '0.0s';
});

resetSubsBtn.addEventListener('click', () => {
  state.subtitles.cues = [];
  state.subtitles.delay = 0.0;
  state.subtitles.fileName = '';
  activeSubFile.textContent = 'No subtitle file loaded';
  subDelayVal.textContent = '0.0s';
  subtitleText.style.display = 'none';
  state.subtitles.enabled = false;
  subtitlesToggle.classList.remove('active');
  
  subFontSize.selectedIndex = 2; // Regular
  subColor.selectedIndex = 0; // White
  subBgOpacity.selectedIndex = 2; // Charcoal
  applySubtitleStyles();
});

[subFontSize, subColor, subBgOpacity].forEach(select => {
  select.addEventListener('change', applySubtitleStyles);
});

// Bookmarks note form interactions
addBookmarkBtn.addEventListener('click', addBookmark);
bookmarkTitleInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    addBookmark();
  }
});

// Library Folder scanner interactions
scanFolderBtn.addEventListener('click', scanFolderAction);

// Render Keyboard Shortcuts tab interface
const renderShortcutsDOM = () => {
  customShortcutsList.innerHTML = '';
  
  for (const action in state.keybindings) {
    const bind = state.keybindings[action];
    const isRebinding = state.rebindingAction === action;
    
    const item = document.createElement('div');
    item.className = 'shortcut-item';
    item.innerHTML = `
      <span class="shortcut-desc">${bind.label}</span>
      <span class="shortcut-key ${isRebinding ? 'active' : ''}" style="cursor: pointer;" title="Click to rebind">
        ${isRebinding ? 'Press any key...' : bind.display}
      </span>
    `;
    
    // Bind click to trigger rebinding state
    item.querySelector('.shortcut-key').addEventListener('click', () => {
      state.rebindingAction = action;
      renderShortcutsDOM();
    });
    
    customShortcutsList.appendChild(item);
  }
};

// Reset custom shortcuts bindings
resetShortcutsBtn.addEventListener('click', () => {
  state.keybindings = JSON.parse(JSON.stringify(DEFAULT_KEYBINDINGS));
  state.rebindingAction = null;
  saveKeybindings();
  renderShortcutsDOM();
});

// Prevent clicked buttons from retaining focus and stealing keyboard shortcuts.
// This is done via pointerdown so that keyboard navigation (tabbing) is unaffected.
document.addEventListener('pointerdown', (e) => {
  const btn = e.target.closest('button');
  if (btn) {
    setTimeout(() => {
      if (document.activeElement === btn) {
        btn.blur();
      }
    }, 50);
  }
});

// Keyboard controls interceptor & Custom Rebinding Listener
window.addEventListener('keydown', (e) => {
  // If we are currently rebinding a key, capture and save
  if (state.rebindingAction) {
    e.preventDefault();
    e.stopPropagation();
    
    const ignoreKeys = ['shift', 'control', 'alt', 'meta', 'capslock'];
    const pressed = e.key.toLowerCase();
    if (ignoreKeys.includes(pressed)) return;
    
    // Format visual display label
    let displayStr = '';
    if (e.ctrlKey) displayStr += 'Ctrl + ';
    if (e.altKey) displayStr += 'Alt + ';
    if (e.shiftKey && e.key !== 'Shift') displayStr += 'Shift + ';
    
    let keyCodeName = e.key;
    if (e.code === 'Space') keyCodeName = 'Space';
    else if (e.key === ' ') keyCodeName = 'Space';
    else if (e.key.startsWith('Arrow')) keyCodeName = e.key.replace('Arrow', '') + ' Arrow';
    else if (keyCodeName.length === 1) keyCodeName = keyCodeName.toUpperCase();
    
    displayStr += keyCodeName;
    
    const action = state.rebindingAction;
    state.keybindings[action] = {
      label: DEFAULT_KEYBINDINGS[action].label,
      key: e.key.toLowerCase(),
      code: e.code,
      shift: e.shiftKey,
      ctrl: e.ctrlKey,
      alt: e.altKey,
      display: displayStr
    };
    
    state.rebindingAction = null;
    saveKeybindings();
    renderShortcutsDOM();
    return;
  }

  const activeEl = document.activeElement;
  const activeTag = activeEl ? activeEl.tagName.toLowerCase() : '';
  
  // DO NOT trigger shortcuts when typing inside text inputs, textareas, select dropdowns, or contenteditable fields!
  if (activeTag === 'textarea' || activeTag === 'select' || (activeEl && activeEl.isContentEditable)) {
    return;
  }
  
  if (activeTag === 'input') {
    const type = (activeEl.type || 'text').toLowerCase();
    const textTypes = ['text', 'search', 'password', 'email', 'number', 'url', 'tel', 'date', 'datetime-local', 'month', 'week', 'time'];
    if (textTypes.includes(type)) {
      return;
    }
  }

  const pressedKey = e.key.toLowerCase();
  const pressedCode = e.code;

  // If focus is on a button, bypass Enter key to let the button activate naturally, but let Space trigger play/pause globally
  if (activeTag === 'button') {
    if (pressedKey === 'enter') {
      return;
    }
  }

  // If focus is on a range slider, bypass arrow keys to let the slider adjust its value
  if (activeTag === 'input' && activeEl.type === 'range') {
    const arrowKeys = ['arrowleft', 'arrowright', 'arrowup', 'arrowdown'];
    if (arrowKeys.includes(pressedKey)) {
      return;
    }
  }

  const isShift = e.shiftKey;
  const isCtrl = e.ctrlKey;
  const isAlt = e.altKey;

  // Helper matching function
  const matchAction = (action) => {
    const bind = state.keybindings[action];
    if (!bind) return false;
    
    // Space bar edge case
    if (bind.code === 'Space' && pressedCode === 'Space') {
      return (!!bind.shift === isShift) && (!!bind.ctrl === isCtrl) && (!!bind.alt === isAlt);
    }
    
    return (bind.key === pressedKey) && (!!bind.shift === isShift) && (!!bind.ctrl === isCtrl) && (!!bind.alt === isAlt);
  };

  // Perform actions based on custom mappings match
  if (matchAction('playPause')) {
    e.preventDefault();
    togglePlay();
  } else if (matchAction('mute')) {
    e.preventDefault();
    toggleMute();
  } else if (matchAction('fullscreen')) {
    e.preventDefault();
    toggleFullscreen();
  } else if (matchAction('pip')) {
    e.preventDefault();
    togglePiP();
  } else if (matchAction('subtitles')) {
    e.preventDefault();
    subtitlesToggle.click();
  } else if (matchAction('seekBack')) {
    e.preventDefault();
    video.currentTime = Math.max(0, video.currentTime - 5);
  } else if (matchAction('seekFwd')) {
    e.preventDefault();
    video.currentTime = Math.min(video.duration || 0, video.currentTime + 5);
  } else if (matchAction('seekBack10')) {
    e.preventDefault();
    video.currentTime = Math.max(0, video.currentTime - 10);
  } else if (matchAction('seekFwd10')) {
    e.preventDefault();
    video.currentTime = Math.min(video.duration || 0, video.currentTime + 10);
  } else if (matchAction('volUp')) {
    e.preventDefault();
    updateVolume(Math.min(1, video.volume + 0.05));
    triggerCentralIndicator('volume-up');
  } else if (matchAction('volDown')) {
    e.preventDefault();
    updateVolume(Math.max(0, video.volume - 0.05));
    triggerCentralIndicator('volume-down');
  } else if (matchAction('next')) {
    e.preventDefault();
    nextVideo();
  } else if (matchAction('prev')) {
    e.preventDefault();
    prevVideo();
  } else if (matchAction('shuffle')) {
    e.preventDefault();
    toggleShuffle();
  } else if (matchAction('repeat')) {
    e.preventDefault();
    toggleRepeatMode();
  } else if (matchAction('abLoop')) {
    e.preventDefault();
    toggleABLoop();
  } else if (/^[0-9]$/.test(pressedKey)) {
    // 0-9 numerical seek keys
    e.preventDefault();
    const percent = parseInt(pressedKey) * 10;
    if (Number.isFinite(video.duration) && video.duration > 0) {
      video.currentTime = (percent / 100) * video.duration;
    }
  }
});

// App startup execution
loadVideo(0);
applySubtitleStyles();
renderPlaylistDOM();
renderShortcutsDOM();
autoScanSavedFolder();

// Apply loaded theme and accent colors at boot
applyTheme(state.theme);
applyAccentColor(state.accent);

// Apply normalizer checkbox state
const normToggle = document.getElementById('normalizer-toggle');
if (normToggle) {
  normToggle.checked = state.normalizerEnabled;
}

// ==========================================================================
// ELECTRON DESKTOP CUSTOM TITLEBAR INTEGRATION & NATIVE DIALOGS
// ==========================================================================

if (ipcRenderer) {
  // Minimize window click
  document.getElementById('titlebar-minimize').addEventListener('click', () => {
    ipcRenderer.send('window-minimize');
  });

  // Maximize/Restore window click
  document.getElementById('titlebar-maximize').addEventListener('click', () => {
    ipcRenderer.send('window-maximize');
  });

  // Close app window click
  document.getElementById('titlebar-close').addEventListener('click', () => {
    ipcRenderer.send('window-close');
  });

  // Replace file browse click behavior to use native OS file dialog picker
  const browseFilesBtn = document.querySelector('.file-upload-btn');
  if (browseFilesBtn) {
    const nativeBrowseBtn = browseFilesBtn.cloneNode(true);
    browseFilesBtn.parentNode.replaceChild(nativeBrowseBtn, browseFilesBtn);

    nativeBrowseBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      try {
        const filePaths = await ipcRenderer.invoke('open-file-dialog');
        if (filePaths && filePaths.length > 0) {
          filePaths.forEach(filePath => {
            const pathParts = filePath.split(/[\\/]/);
            const fileName = pathParts[pathParts.length - 1];
            
            // Format file URL for Windows or Unix local absolute path compatibility
            const cleanPath = filePath.replace(/\\/g, '/');
            const fileUrl = cleanPath.startsWith('/') ? `file://${cleanPath}` : `file:///${cleanPath}`;
            
            addPlaylistVideo(fileName, fileUrl, 'PC Local File');
          });
        }
      } catch (err) {
        console.error('Error selecting files from native dialog', err);
      }
    });
  }

  // Global OS media hotkeys integrations
  ipcRenderer.on('global-play-pause', () => togglePlay());
  ipcRenderer.on('global-next-track', () => nextVideo());
  ipcRenderer.on('global-prev-track', () => prevVideo());
} else {
  // Hide custom titlebar if running outside Electron (i.e. normal web browser fallback)
  const titlebar = document.getElementById('custom-titlebar');
  if (titlebar) {
    titlebar.style.display = 'none';
  }
  document.body.classList.add('web-mode');
  const appShell = document.getElementById('app');
  if (appShell) {
    appShell.style.height = '100vh';
    appShell.style.minHeight = '100vh';
  }
}

