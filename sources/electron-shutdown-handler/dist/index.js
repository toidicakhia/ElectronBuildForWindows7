"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const node_events_1 = require("node:events");
const SUPPORTED_PLATFORMS = ['win32'];
let addon = null;
if (SUPPORTED_PLATFORMS.includes(process.platform)) {
    addon = require('../build/Release/PaymoWinShutdownHandler.node'); // eslint-disable-line import/no-dynamic-require
}
class ElectronShutdownHandlerClass extends node_events_1.EventEmitter {
    constructor() {
        super();
        this.on('newListener', (event) => {
            if (event == 'shutdown' && this.listenerCount('shutdown') == 0) {
                // create native listener
                if (addon) {
                    addon.insertWndProcHook(() => {
                        this.emit('shutdown');
                    });
                }
            }
        });
        this.on('removeListener', (event) => {
            if (event == 'shutdown' && this.listenerCount('shutdown') == 0) {
                // remove native listener
                if (addon) {
                    addon.removeWndProcHook();
                }
            }
        });
    }
    setWindowHandle(handle) {
        if (!addon) {
            return;
        }
        addon.setMainWindowHandle(handle);
    }
    blockShutdown(reason) {
        if (!addon) {
            return false;
        }
        return addon.acquireShutdownBlock(reason);
    }
    releaseShutdown() {
        if (!addon) {
            return false;
        }
        return addon.releaseShutdownBlock();
    }
}
const ElectronShutdownHandler = new ElectronShutdownHandlerClass();
exports.default = ElectronShutdownHandler;
