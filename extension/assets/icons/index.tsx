import React from "react";
import { CSSProperties } from "styled-components";

/**
 * EHRIcon.
 *
 * @param {object} props Properties.
 * @param {CSSProperties | undefined} props.style Style properties.
 * @returns {React.ReactElement} React element.
 */
export function EHRIcon({ style }: { style?: CSSProperties }): JSX.Element {
  return (
    <img
      style={style}
      src="https://app.voiston.ai/assets/icon/VOISTON_ICONS-16.svg"
      alt="Prontuários"
    />
  );
}

/**
 * ExamIcon.
 *
 * @param {object} props Properties.
 * @param {CSSProperties | undefined} props.style Style properties.
 * @returns {React.ReactElement} React element.
 */
export function ExamIcon({ style }: { style?: CSSProperties }): JSX.Element {
  return (
    <img
      style={style}
      src="https://app.voiston.ai/assets/icon/VOISTON_ICONS-11.svg"
      alt="Exames"
    />
  );
}
