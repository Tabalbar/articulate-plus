import {atom} from 'recoil'

export const transcriptState = atom({
    key: 'transcriptState', // unique ID (with respect to other atoms/selectors)
    default: '', // default value (aka initial value)
  });


