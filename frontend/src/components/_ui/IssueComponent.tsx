import api from "@/utils/api";
import * as React from "react";
import { Pie, PieChart } from "recharts";
import Notification from "@/Notification";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/_ui/card";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
} from "@/components/_ui/chart";

import { secondsToHMSorDays } from "@/utils/timeFormate";

const chartConfig = {
  visitors: {
    label: "Visitors",
  },
  chrome: {
    label: "Chrome",
    color: "hsl(var(--chart-1))",
  },
  safari: {
    label: "Safari",
    color: "hsl(var(--chart-2))",
  },
  firefox: {
    label: "Firefox",
    color: "hsl(var(--chart-3))",
  },
  edge: {
    label: "Edge",
    color: "hsl(var(--chart-4))",
  },
  other: {
    label: "Other",
    color: "hsl(var(--chart-5))",
  },
} satisfies ChartConfig;

type ChartData = {
  _id: string;
  total_time: number;
  total_duration: number;
  percentage: number;
  fill: string;
};

interface Props {
  selectedIssueId: number;
}

const IssueComponent: React.FC<Props> = ({ selectedIssueId }) => {
  const getColor = (data: ChartData[]) => {
    const colors = ["#FF6633", "#2563eb", "#FF33FF", "#FFFF99", "#00B3E6"];
    return data.map((entry, index) => ({
      ...entry,
      fill: colors[index % colors.length],
    }));
  };

  const [chartData, setChartData] = React.useState<ChartData[]>([]);
  React.useEffect(() => {
    api
      .post(`/get_user_total_duration_time`, {
        issue_id: selectedIssueId,
      })
      .then((response) => {
        const data = response.data;
        if (!data.status) {
          Notification({ message: data.message, type: "error" });
          return;
        }

        setChartData(getColor(data.data));
        console.log(getColor(data.data));
      })
      .catch((_error) => {
        Notification({ message: "Problem fetching data", type: "error" });
      });
  }, [selectedIssueId]);

  return (
    <div className="flex space-x-4">
      <Card className="w-1/2">
        <CardHeader className="flex items-center justify-between pb-0">
          <div>
            <CardTitle>User Work Time</CardTitle>
            <CardDescription>
              Time spent by each user on this issue
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent className="flex-1 pb-0">
          <ChartContainer
            config={chartConfig}
            className="mx-auto aspect-square max-h-[250px]"
          >
            <PieChart>
              <ChartTooltip
                cursor={false}
                content={<ChartTooltipContent hideLabel />}
              />
              <Pie
                data={chartData}
                dataKey="percentage"
                nameKey="_id"
                innerRadius={40}
              />
              {chartData.map((entry) => (
                <ChartLegend key={entry._id} color={entry.fill} />
              ))}
            </PieChart>
          </ChartContainer>
        </CardContent>
      </Card>
      <div className="w-1/2">
        <div className="max-h-[400px] overflow-y-auto">
          <table className="table-auto w-full text-left">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Count
                </th>
                <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Duration
                </th>
                <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Percentage
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {chartData.map((data) => (
                <tr key={data._id}>
                  <td
                    className="px-4 py-2 text-center"
                    style={{ color: data.fill }}
                  >
                    {data._id}
                  </td>
                  <td className="px-4 py-2 text-center">{data.total_time}</td>
                  <td className="px-4 py-2 text-center">
                    {secondsToHMSorDays(data.total_duration)}
                  </td>
                  <td className="px-4 py-2 text-center">
                    {data.percentage.toFixed(2)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default IssueComponent;
