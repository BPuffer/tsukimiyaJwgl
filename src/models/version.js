import { version } from '../../package.json';

const [MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION] = version.split('.').map(Number);
const BUILD_VERSION = 0;

const MAJOR_LICENSE_VERSION = 0;
const MINOR_LICENSE_VERSION = 1;


function versionStr(ma, mi, pa, bu) {
  return `${ma}.${mi}.${pa}.${bu}`
}

function versionInt(ma, mi, pa, bu) {
  return ma * 1_00_00_00 + mi * 1_00_00 + pa * 1_00 + bu
}


const VERSION = versionStr(MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION, BUILD_VERSION)
const VERSION_INT = versionInt(MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION, BUILD_VERSION)
const LICENSE_VERSION = `${MAJOR_LICENSE_VERSION}.${MINOR_LICENSE_VERSION}`
const LICENSE_VERSION_INT = versionInt(0, 0, MAJOR_LICENSE_VERSION, MINOR_LICENSE_VERSION)


export {
  VERSION,
  VERSION_INT,
  LICENSE_VERSION,
  LICENSE_VERSION_INT,
  versionStr,
  versionInt
}
