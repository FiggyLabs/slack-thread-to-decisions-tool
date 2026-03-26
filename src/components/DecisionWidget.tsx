import React from 'react';
import { Decision } from '@/types';

interface DecisionWidgetProps {
  decision: Decision;
}

const DecisionWidget: React.FC<DecisionWidgetProps> = ({ decision }) => {
  return (
    <div style={{ border: '1px solid #ccc', padding: '10px', margin: '10px' }}>
      <p>{decision.text}</p>
      {decision.actions.map((action, index) => (
        <button key={index} onClick={action.onClick}>
          {action.label}
        </button>
      ))}
    </div>
  );
};

export default DecisionWidget;
