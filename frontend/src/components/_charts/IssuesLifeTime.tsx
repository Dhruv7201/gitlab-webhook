import * as React from "react";
import { useNavigate } from "react-router-dom";
import api from "@/utils/api";
import {
  Bar,
  BarChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from "recharts";
import Notification from "../../Notification";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/_ui/card";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltipContent,
} from "@/components/_ui/chart";

type ChartData = {
  issue: string;
  [key: string]: number | string;
};

interface Props {
  selectedProjectId: number;
}

type MilestoneData = {
  id: number;
  title: string;
  total_time: number;
  assign_time: number;
};

const getColor = (index: number) => {
  const colors = [
    "hsl(var(--chart-1))",
    "hsl(var(--chart-2))",
    "hsl(var(--chart-3))",
    "hsl(var(--chart-4))",
  ];
  return colors[index % colors.length];
};

const formatDuration = (seconds: number) => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.round(seconds % 60);

  return `${hours.toString().padStart(2, "0")}:${minutes
    .toString()
    .padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
};

const CustomTooltip = ({ payload, label, chartConfig }: any) => {
  if (!payload || payload.length === 0) return null;

  const issueTitle = label;
  const data = payload[0]?.payload;

  return (
    <div
      style={{
        backgroundColor: "#fff",
        border: "1px solid #ddd",
        padding: "10px",
        borderRadius: "4px",
      }}
    >
      <p className="label">{issueTitle}</p>
      {Object.keys(data).map((key) =>
        key !== "issue" ? (
          <p
            key={key}
            className="intro"
            style={{ color: data[key] ? "#000" : "#ccc" }}
          >
            {chartConfig[key]?.label}: {formatDuration(data[key] as number)}
          </p>
        ) : null
      )}
    </div>
  );
};

const IssuesLifeTime: React.FC<Props> = ({ selectedProjectId }) => {
  const [chartData, setChartData] = React.useState<ChartData[]>([]);
  const [chartConfig, setChartConfig] = React.useState<ChartConfig>({});
  const [milestones, setMilestones] = React.useState<MilestoneData[]>([]);
  const [selectedMilestone, setSelectedMilestone] = React.useState<number>(0);
  const navigate = useNavigate();

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
    api
      .post(`/issue_lifetime`, {
        project_id: selectedProjectId,
        milestone_id: selectedMilestone,
      })
      .then((response) => {
        const data = response.data;
        if (data.status === false) {
          Notification({ message: data.message, type: "error" });
          return;
        }

        // Extract unique labels and create dynamic chartConfig
        const uniqueLabels = new Set<string>();
        const transformedData = data.data.map((issue: any) => {
          const labelDurations = issue.work.reduce((acc: any, cur: any) => {
            uniqueLabels.add(cur.label);
            acc[cur.label] = (acc[cur.label] || 0) + cur.duration;
            return acc;
          }, {});
          return {
            issue: issue.title,
            issueId: issue.id,
            ...labelDurations,
          };
        });

        const dynamicChartConfig = Array.from(uniqueLabels).reduce(
          (acc: ChartConfig, label: string, index: number) => {
            acc[label] = {
              label: label,
              color: getColor(index),
            };
            return acc;
          },
          {}
        );

        setChartData(transformedData);
        setChartConfig(dynamicChartConfig);
      })
      .catch((_error: any) => {
        Notification({ message: "Problem fetching issues", type: "error" });
      });
  }, [selectedProjectId, selectedMilestone]);

  const handleBarClick = (data: any) => {
    console.log("data", data);
    const issueId = data.issueId;
    navigate(`/issue/${issueId}`);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle>Bar Chart - User Issue Durations</CardTitle>
          <div className="flex items-center gap-4">
            <select
              className="p-2 text-sm rounded-md"
              onChange={(e) => setSelectedMilestone(Number(e.target.value))}
              value={selectedMilestone}
            >
              <option value={0}>Select Milestone</option>
              {milestones.map((milestone) => (
                <option key={milestone.id} value={milestone.id}>
                  {milestone.title}
                </option>
              ))}
            </select>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <BarChart
            data={chartData}
            margin={{
              top: 20,
              right: 20,
              bottom: 30,
              left: 20,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="issue"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              angle={-20}
              textAnchor="end"
              tickFormatter={(value) =>
                value.length > 20 ? value.slice(0, 20) + "..." : value
              }
            />
            <YAxis tickFormatter={(value) => formatDuration(value)} />
            <Tooltip content={<CustomTooltip chartConfig={chartConfig} />} />
            <Legend />
            {Object.keys(chartConfig).map((key, index) => (
              <Bar
                key={index}
                dataKey={key}
                fill={chartConfig[key].color}
                stackId="a"
                radius={[4, 4, 0, 0]}
                onClick={handleBarClick}
              />
            ))}
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
};

export default IssuesLifeTime;
