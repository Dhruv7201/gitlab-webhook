import * as React from "react";
import api from "@/utils/api";
import { Area, AreaChart, CartesianGrid, XAxis } from "recharts";
import Notification from "../../Notification";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/_ui/card";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
} from "@/components/_ui/chart";

type ChartData = {
  labels: string[];
  completed_issues: number[];
  assigned_issues: number[];
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

  React.useEffect(() => {

    api
      .post(`/user_activity_chart`, {
        project_id: selectedProjectId,
      })
      .then((response) => {
        const data = response.data;
        if (data.status == false) {
          Notification({ message: data.message, type: "error" });
          return;
        }
        const transformedData = data.data.labels.map(
          (label: string, index: number) => ({
            user: label,
            completed_issues: data.data.completed_issues[index],
            assigned_issues: data.data.assigned_issues[index],
          })
        );
        setChartData(transformedData);
      })
      .catch((_error: any) => {
        Notification({ message: "Problem fetching users", type: "error" });
      });
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

            {chartData.map((_entry, index) => (
              <ChartLegend key={index} color="var(--color-desktop)" />
            ))}
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
};
export default AreaChartCom;
