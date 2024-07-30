import React, { useState, useEffect } from 'react';
import api from '@/utils/api';

interface Milestone {
  title: string;
  start_date: string;
  due_date: string;
  web_url: string; // Correct field name
}

interface MilestoneData {
  ongoing_milestones: Milestone[];
  completed_milestones: Milestone[];
  all_milestones: Milestone[];
}

const MilestoneTabs: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'ongoing' | 'completed' | 'all'>('ongoing');
  const [milestones, setMilestones] = useState<MilestoneData>({
    ongoing_milestones: [],
    completed_milestones: [],
    all_milestones: []
  });

  useEffect(() => {
    const fetchMilestones = async () => {
      try {
        const response = await api.get('/milestones');
        const { data } = response;

        if (data && data.data) {
          setMilestones(data.data);
        } else {
          console.error('Unexpected data format:', data);
        }
      } catch (error) {
        console.error('Error fetching milestones:', error);
      }
    };

    fetchMilestones();
  }, []);

  const renderMilestones = () => {
    if (!milestones) return <div>Loading...</div>;

    // Use optional chaining and default to empty array
    const itemsToDisplay = milestones[`${activeTab}_milestones`] || [];

    return (
      <ul>
        {itemsToDisplay.length > 0 ? (
          itemsToDisplay.map((milestone, index) => (
            <li key={index} style={{ marginBottom: '20px' }}>
              <h3>{milestone.title}</h3>
              <p><strong>Start Date:</strong> {milestone.start_date}</p>
              <p><strong>Due Date:</strong> {milestone.due_date}</p>
              <a href={milestone.web_url} target="_blank" rel="noopener noreferrer">More Details</a>
            </li>
          ))
        ) : (
          <p>No milestones available</p>
        )}
      </ul>
    );
  };

  return (
    <div>
      <div>
        <button
          onClick={() => setActiveTab('ongoing')}
          style={{ marginRight: '10px', padding: '10px', cursor: 'pointer', backgroundColor: activeTab === 'ongoing' ? 'lightblue' : 'white' }}
        >
          Ongoing
        </button>
        <button
          onClick={() => setActiveTab('completed')}
          style={{ marginRight: '10px', padding: '10px', cursor: 'pointer', backgroundColor: activeTab === 'completed' ? 'lightblue' : 'white' }}
        >
          Completed
        </button>
        <button
          onClick={() => setActiveTab('all')}
          style={{ padding: '10px', cursor: 'pointer', backgroundColor: activeTab === 'all' ? 'lightblue' : 'white' }}
        >
          All
        </button>
      </div>
      <div>
        {renderMilestones()}
      </div>
    </div>
  );
};

export default MilestoneTabs;
