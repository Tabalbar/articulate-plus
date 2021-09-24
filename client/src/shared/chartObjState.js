import { RecoilRoot, atom, selector, useRecoilState } from "recoil";

const { default: ChartObj } = require("./ChartObj");
export const chartObjState = atom({
  key: "chartObjState",
  default: ChartObj.initialize(),
});
