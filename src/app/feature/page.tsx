import React, { useEffect, useState } from 'react';
import axios from 'axios';
import DecisionWidget from '@/components/DecisionWidget';

const SlackThreadPage = () => {
  const [decisions, setDecisions] = useState<any[]>([]);

  useEffect(() => {
    const fetchSlackThreads = async () => {
      try {
        const response = await axios.get('/api/fetchSlackThreads');
        const messages = response.data.messages;
        const parsedDecisions = parseDecisions(messages);
        setDecisions(parsedDecisions);
      } catch (error) {
        console.error('Error fetching Slack threads:', error);
      }
    };

    fetchSlackThreads();
  }, []);

  const parseDecisions = (messages: any[]) => {
    return messages
      .filter((message) => message.text.includes('decision') || message.text.includes('action item'))
      .map((message) => ({
        id: message.ts,
        text: message.text,
        actions: [
          { label: 'Mark as Done', onClick: () => handleAction(message, 'done') },
          { label: 'Assign', onClick: () => handleAction(message, 'assign') },
        ],
      }));
  };

  const handleAction = (message: any, action: string) => {
    // Implement logic to perform the action on the Slack thread
    console.log(`Handling ${action} for message:`, message);
  };

  return (
    <div>
      {decisions.map((decision) => (
        <DecisionWidget key={decision.id} decision={decision} />
      ))}
    </div>
  );
};

export default SlackThreadPage;
