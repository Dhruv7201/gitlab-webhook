import * as React from "react";
import { Area, AreaChart, CartesianGrid, XAxis } from "recharts";
import Notification from "../../Notification";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

type ChartData = {
  user: string;
  completed_issues: number;
  assigned_issues: number;
};

const chartConfig = {
  mobile: {
    label: "assigned_issues",
    color: "hsl(var(--chart-2))",
  },
  desktop: {
    label: "completed_issues",
    color: "hsl(var(--chart-1))",
  },
} as ChartConfig;

interface Props {
  selectedProjectId: number;
}

const AreaChartCom: React.FC<Props> = ({ selectedProjectId }) => {
  const [chartData, setChartData] = React.useState<ChartData[]>([]);
  const api = import.meta.env.VITE_API_URL;

  React.useEffect(() => {
    const fetchData = async () => {
      if (selectedProjectId === 0) return;
      try {
        const response = await fetch(
          api + `/user_activity_chart/${selectedProjectId}`
        );
        const data = await response.json();
        if (data.status == false) {
          Notification({ message: data.message, type: "error" });
          return;
        }

        const actual_data = data.data;
        const transformedData = actual_data.labels.map(
          (label: string, index: number) => ({
            user: label,
            completed_issues: actual_data.completed_issues[index],
            assigned_issues: actual_data.assigned_issues[index],
          })
        );

        setChartData(transformedData);
      } catch (error) {
        Notification({ message: "Problem fetching users", type: "error" });
      }
    };

    fetchData();
  }, [selectedProjectId]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>User Issue Count</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <AreaChart
            accessibilityLayer
            data={chartData}
            margin={{
              left: 20,
              right: 20,
            }}
          >
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="user"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              tickFormatter={(value) => value.slice(0, 3)}
            />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent indicator="line" />}
            />
            <Area
              dataKey="completed_issues"
              type="natural"
              fill="var(--color-desktop)"
              fillOpacity={0.4}
              stroke="var(--color-desktop)"
              stackId="a"
            />

            <Area
              dataKey="assigned_issues"
              type="natural"
              fill="var(--color-mobile)"
              fillOpacity={0.4}
              stroke="var(--color-mobile)"
              stackId="a"
            />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
};
export default AreaChartCom;
