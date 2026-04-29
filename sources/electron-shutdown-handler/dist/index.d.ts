/// <reference types="node" />
/// <reference types="node" />
import { EventEmitter } from 'node:events';
declare class ElectronShutdownHandlerClass extends EventEmitter {
    constructor();
    setWindowHandle(handle: Buffer): void;
    blockShutdown(reason: string): boolean;
    releaseShutdown(): boolean;
}
declare const ElectronShutdownHandler: ElectronShutdownHandlerClass;
export default ElectronShutdownHandler;
