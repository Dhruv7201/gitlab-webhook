import * as React from "react";
import api from "@/utils/api";
import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  XAxis,
  Tooltip,
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
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/_ui/chart";

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
  title: string;
  total_duration: number; // Assuming this is in seconds
};

interface Props {
  selectedProjectId: number;
}

const WorkBarChart: React.FC<Props> = ({ selectedProjectId }) => {
  const [barData, setBarData] = React.useState<BarData[]>([]);

  React.useEffect(() => {
    api
      .post(`/work_duration_by_task`, {
        project_id: selectedProjectId,
      })
      .then((response) => {
        const data = response.data;
        if (data.status === false) {
          Notification({ message: data.message, type: "error" });
          return;
        }
        setBarData(data.data);
      })
      .catch(() => {
        Notification({ message: "Problem fetching users", type: "error" });
      });
  }, [selectedProjectId]);

  const renderLabel = (value: number) => {
    const seconds = value;
    const hr = Math.floor(seconds / 3600)
      .toString()
      .padStart(2, "0");
    const min = Math.floor((seconds % 3600) / 60)
      .toString()
      .padStart(2, "0");
    const sec = Math.floor(seconds % 60)
      .toString()
      .padStart(2, "0");

    return `${hr}:${min}:${sec}`;
  };

  const renderTooltipContent = (props: any) => {
    if (!props.active || !props.payload || props.payload.length === 0)
      return null;

    const { payload } = props;
    const { title, total_duration } = payload[0].payload;

    return (
      <div className="bg-white border border-gray-300 p-2 rounded">
        <p>
          <strong>Time:</strong> {renderLabel(total_duration)}
        </p>
        <p>
          <strong>Name:</strong> {title || "No Name"}
        </p>{" "}
        {/* Fallback for missing name */}
      </div>
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
              tickFormatter={(value) =>
                value.length > 10 ? value.slice(0, 10) + "..." : value
              }
            />
            <Tooltip content={renderTooltipContent} />
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
