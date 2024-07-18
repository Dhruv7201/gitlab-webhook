import * as React from "react";
import { Bar, BarChart, CartesianGrid, LabelList, XAxis } from "recharts";
import Notification from "../../Notification";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "hsl(var(--chart-1))",
    format: "time_formats",
  },
} as ChartConfig;

type BarData = {
  name: string;
  time_waste: string;
  format: any;
};

interface Props {
  selectedProjectId: number;
}

const WorkBarChart: React.FC<Props> = ({ selectedProjectId }) => {
  const api = import.meta.env.VITE_API_URL;

  const [barData, setBarData] = React.useState<BarData[]>([]);

  React.useEffect(() => {
    if (selectedProjectId === 0) return;
    const fetchData = async () => {
      try {
        const response = await fetch(api + `/work_duration_by_task`, {
          method: "POST",
          body: JSON.stringify({
            project_id: selectedProjectId,
          }),
          headers: {
            "Content-type": "application/json; charset=UTF-8",
          },
        });
        const data = await response.json();
        if (data.status == false) {
          Notification({ message: data.message, type: "error" });
          return;
        }

        setBarData(data.data);
      } catch (error) {
        Notification({ message: "Problem fetching users", type: "error" });
      }
    };
    fetchData();
  }, [selectedProjectId]);

  const renderLabel = (props: any) => {
    const seconds = props;
    var min = null;
    var hr = null;
    var sec = null;

    hr = Math.floor(seconds / 3600);
    if (hr == 0) {
      hr = "00";
    }

    min = Math.floor((seconds % 3600) / 60);
    if (min == 0) {
      min = "00";
    }

    sec = Math.floor(seconds % 60);

    return `${hr}:${min}:${sec}`;
  };

  const renderLabel1 = (props: any) => {
    const seconds = props;
    var min = null;
    var hr = null;
    var sec = null;

    hr = Math.floor(seconds / 3600);
    if (hr == 0) {
      hr = "00";
    }

    min = Math.floor((seconds % 3600) / 60);
    if (min == 0) {
      min = "00";
    }

    sec = Math.floor(seconds % 60);

    return (
      <p>
        <li className="marker:text-green-600">
          Time {hr}:{min}:{sec}
        </li>
      </p>
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Task Duration</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <BarChart
            accessibilityLayer
            data={barData}
            margin={{
              top: 20,
            }}
          >
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="title"
              tickLine={false}
              tickMargin={10}
              axisLine={false}
              tickFormatter={(value) => value}
            />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent hideLabel />}
              formatter={renderLabel1}
            />
            <Bar
              dataKey="total_duration"
              fill="var(--color-desktop)"
              radius={8}
            >
              <LabelList
                position="top"
                offset={12}
                className="fill-foreground"
                fontSize={12}
                formatter={renderLabel}
              />
            </Bar>
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
};

export default WorkBarChart;
