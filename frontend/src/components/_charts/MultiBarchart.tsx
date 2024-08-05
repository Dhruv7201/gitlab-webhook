import React from "react";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Tooltip } from "recharts";
import api from "@/utils/api";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/_ui/card";
import { ChartConfig, ChartContainer } from "@/components/_ui/chart";
import { secondsToHMSorDays } from "@/utils/timeFormate";

const chartConfig = {
  total_time: {
    label: "Total Time",
    color: "hsl(var(--chart-1))",
  },
  assign_time: {
    label: "Assigned Time",
    color: "hsl(var(--chart-2))",
  },
} satisfies ChartConfig;

type Milestone = {
  id: number;
  title: string;
  start_date: string;
  due_date: string;
  web_url: string;
};

type MilestoneData = {
  title: string;
  total_time: number;
  assign_time: number;
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const { total_time, assign_time } = payload[0].payload;
    return (
      <div className="custom-tooltip p-2 bg-white border border-gray-200 shadow-md rounded-md">
        <p className="label">{`Title: ${label}`}</p>
        <p className="intro">{`Total Time: ${secondsToHMSorDays(
          total_time
        )}`}</p>
        <p className="intro">{`Assigned Time: ${secondsToHMSorDays(
          assign_time
        )}`}</p>
      </div>
    );
  }

  return null;
};

export function MultiBarChart({ project_id }: { project_id: number }) {
  const [milestones, setMilestones] = React.useState<Milestone[]>([]);
  const [chartData, setChartData] = React.useState<MilestoneData[]>([]);
  const [selectedMilestone, setSelectedMilestone] = React.useState<number>(0);

  React.useEffect(() => {
    const fetchMilestones = async () => {
      try {
        const response = await api.post("/active_milestones");
        const { data } = response;

        if (data && data.data) {
          setMilestones(data.data);
        } else {
          console.error("Unexpected data format:", data);
        }
      } catch (error) {
        console.error("Error fetching milestones:", error);
      }
    };

    fetchMilestones();
  }, []);

  React.useEffect(() => {
    if (selectedMilestone !== null) {
      const fetchChartData = async () => {
        try {
          const response = await api.post("/milestone_issues", {
            project_id: project_id,
            milestone_id: selectedMilestone,
          });
          const { data } = response;

          if (data && data.data) {
            setChartData(data.data);
          } else {
            console.error("Unexpected data format:", data);
          }
        } catch (error) {
          console.error("Error fetching chart data:", error);
        }
      };

      fetchChartData();
    }
  }, [selectedMilestone, project_id]);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between w-full">
          <CardTitle>Time Spent on Milestones</CardTitle>
          <select
            className="p-2 text-sm rounded-md"
            onChange={(e) => setSelectedMilestone(Number(e.target.value))}
          >
            <option key={0} value={0}>
              Select Milestone
            </option>
            {milestones.map((milestone) => (
              <option key={milestone.id} value={milestone.id}>
                {milestone.title}
              </option>
            ))}
          </select>
        </div>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <BarChart data={chartData}>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="title"
              tickLine={false}
              tickMargin={10}
              axisLine={false}
              tickFormatter={(value) => {
                const limit = 25;
                return value.length > limit
                  ? `${value.substring(0, limit)}...`
                  : value;
              }}
            />
            <YAxis tickFormatter={secondsToHMSorDays} />
            <Tooltip content={<CustomTooltip />} />
            <Bar
              dataKey="total_time"
              fill={chartConfig.total_time.color}
              radius={4}
            />
            <Bar
              dataKey="assign_time"
              fill={chartConfig.assign_time.color}
              radius={4}
            />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
