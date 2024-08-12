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
import { secondsToHMSorDays } from "@/utils/timeFormate";
import { DateRange } from "react-day-picker";

interface Props {
  selectedProjectId: number;
  dateRange?: DateRange;
}

type ChartData = {
  issue: string;
  [key: string]: number | string;
};

interface Props {
  selectedProjectId: number;
  dateRange?: DateRange;
}

type MilestoneData = {
  id: number;
  title: string;
  total_time: number;
  assign_time: number;
};

const getColor = (label: string) => {
  const colors = [
    "hsl(var(--chart-1))",
    "#ed9121",
    "#e6e6fa",
    "hsl(var(--chart-4))",
  ];
  if (label === "Development") return colors[2];
  if (label === "Testing") return colors[1];
  if (label === "Doing") return colors[0];
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
        key !== "issue" && key !== "issueId" ? (
          <p
            key={key}
            className="intro"
            style={{ color: data[key] ? "#000" : "#ccc" }}
          >
            {chartConfig[key]?.label}: {secondsToHMSorDays(data[key])}
          </p>
        ) : null
      )}
    </div>
  );
};

const IssuesLifeTime: React.FC<Props> = ({ selectedProjectId, dateRange }) => {
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
        all_milestones: milestones.map((milestone) => milestone.id),
        milestone_id: selectedMilestone,
        date_range: dateRange,
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
              color: getColor(label),
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
  }, [selectedProjectId, selectedMilestone, dateRange]);

  const handleBarClick = (data: any) => {
    let issueId = data.issueId;
    if (issueId === undefined) {
      const issue = chartData.find((issue) => issue.title === data.issue);
      if (issue) {
        issueId = issue.issueId;
      }
    }
    navigate(`/issue/${issueId}`);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle>Issues Lifetime</CardTitle>
          <div className="flex items-center gap-4">
            <select
              className="p-3 text-sm rounded-lg border border-gray-300 shadow-sm focus:ring focus:ring-blue-500 focus:border-blue-500 transition duration-200 ease-in-out hover:cursor-pointer min-w-[215px]"
              onChange={(e) => setSelectedMilestone(Number(e.target.value))}
              value={selectedMilestone}
            >
              <option value={0} className="text-gray-500 bg-gray-100">
                Select Milestone
              </option>
              {milestones.map((milestone) => (
                <option
                  key={milestone.id}
                  value={milestone.id}
                  className="text-gray-700 bg-white hover:bg-blue-100"
                >
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
            <CartesianGrid vertical={false} />
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
            <YAxis tickFormatter={(value) => secondsToHMSorDays(value)} />
            <Tooltip content={<CustomTooltip chartConfig={chartConfig} />} />
            <Legend layout="horizontal" verticalAlign="top" align="center" />
            {Object.keys(chartConfig).map((key, index) => (
              <Bar
                className="hover:cursor-pointer"
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
