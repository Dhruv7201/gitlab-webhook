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
  issue_name: string;
  url: string;
  issue_id: number;
  duration: number;
  percentage: number;
  fill: string;
};

interface Props {
  selectedUserId: number;
}

const UserComponent: React.FC<Props> = ({ selectedUserId }) => {
  function getRandomColor(): string {
    const letters = "0123456789ABCDEF";
    let color = "#";
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  }
  const getColor = (data: ChartData[]) => {
    const colors = ["#FF6633", "#2563eb", "#FF33FF", "#3ee66d", "#00B3E6"];
    return data.map((entry, index) => ({
      ...entry,
      fill: index < colors.length ? colors[index] : getRandomColor(),
    }));
  };

  const [chartData, setChartData] = React.useState<ChartData[]>([]);
  React.useEffect(() => {
    api
      .post(`/get_all_issues_duration`, {
        user_id: selectedUserId,
      })
      .then((response) => {
        const data = response.data;
        if (!data.status) {
          Notification({ message: data.message, type: "error" });
          return;
        }
        // short data by duration from high to low
        data.data.sort((a: ChartData, b: ChartData) => b.duration - a.duration);
        setChartData(getColor(data.data));
      })
      .catch((_error) => {
        Notification({ message: "Problem fetching data", type: "error" });
      });
  }, [selectedUserId]);

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
                nameKey="issue_name"
                innerRadius={40}
              />
            </PieChart>
          </ChartContainer>
        </CardContent>
      </Card>
      <Card className="w-1/2">
        <div className="max-h-[400px] overflow-y-auto">
          <table className="table-auto w-full text-left">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
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
                <tr key={data.issue_name}>
                  <td
                    className="px-4 py-2 text-center"
                    style={{ color: data.fill }}
                  >
                    <a
                      href={data.url}
                      className="underline"
                      target="_blank"
                      rel="noreferrer"
                    >
                      {data.issue_name}
                    </a>
                  </td>

                  <td className="px-4 py-2 text-center">
                    {secondsToHMSorDays(data.duration)}
                  </td>
                  <td className="px-4 py-2 text-center">
                    {data.percentage.toFixed(2)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

export default UserComponent;
