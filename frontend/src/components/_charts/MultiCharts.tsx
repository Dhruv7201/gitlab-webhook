import api from '@/utils/api';
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import Notification from '@/Notification';

interface Props {
  selectedProjectId: number;
}

interface PersonDuration {
  person: string;
  duration: number;
}

interface Issue {
  _id: string;
  person_duration: PersonDuration[];
}

// Utility function to truncate string
const truncateString = (str: string, num: number) => {
  if (str.length > num) {
    return str.slice(0, num) + '...';
  }
  return str;
};

// Custom tooltip component
const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const issueData = payload[0].payload;
    return (
      <div className="custom-tooltip">
        <p className="label">{`Issue: ${issueData.fullIssue}`}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} style={{ color: entry.color }}>
            {`${entry.name}: ${entry.value}`}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const MultiCharts = ({ selectedProjectId }: Props) => {
  const [data, setData] = React.useState<Issue[]>([]);
  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7f50', '#8a2be2'];

  React.useEffect(() => {
    api.post('/issue_lifetime', { project_id: selectedProjectId })
      .then(response => {
        console.log(response);
        const data = response.data;
        console.log(data);
        if (data.status === false) {
          Notification({ message: data.message, type: 'error' });
          return;
        }
        setData(data.data);
      })
      .catch(error => {
        Notification({ message: 'Problem fetching users', type: 'error' });
      });
  }, [selectedProjectId]);

  // Extract unique user names for dynamic bar rendering
  const uniqueUsers = [
    ...new Set(data.flatMap(issue => issue.person_duration.map(user => user.person)))
  ];

  // Transform data
  const transformedData = data.map(issue => {
    const result: { [key: string]: any } = {
      issue: truncateString(issue._id, 25),
      fullIssue: issue._id
    };
    issue.person_duration.forEach(user => {
      result[user.person] = user.duration;
    });
    return result;
  });

  return (
    <BarChart width={600} height={400} data={transformedData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="issue" />
      <YAxis />
      <Tooltip content={<CustomTooltip />} />
      <Legend />
      {uniqueUsers.map((user, index) => (
        <Bar key={user} dataKey={user} stackId="a" fill={colors[index % colors.length]} />
      ))}
    </BarChart>
  );
};

export default MultiCharts;
