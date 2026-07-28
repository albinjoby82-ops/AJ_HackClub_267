import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('png');
Config.setCodec('h264');
// High profile + yuv420p + faststart are applied in tools/finalise.mjs, which
// owns the delivery encode. Remotion produces the high-quality master.
Config.setPixelFormat('yuv420p');
Config.setCrf(16);
Config.setOverwriteOutput(true);
Config.setChromiumOpenGlRenderer('angle');
