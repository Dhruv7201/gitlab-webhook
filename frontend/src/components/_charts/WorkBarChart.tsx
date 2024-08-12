import * as React from "react";
import api from "@/utils/api";
import { useNavigate } from "react-router-dom";
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
import { secondsToHMSorDays } from "@/utils/timeFormate";

const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "hsl(var(--chart-1))",
    format: "time_formats",
  },
} as ChartConfig;

type BarData = {
  name: string;
  id: number;
  time_waste: string;
  format: any;
  title: string;
  total_duration: number; // Assuming this is in seconds
};

interface Props {
  selectedProjectId: number;
  dateRange: any;
}

const WorkBarChart: React.FC<Props> = ({ selectedProjectId, dateRange }) => {
  const [barData, setBarData] = React.useState<BarData[]>([]);

  const navigate = useNavigate();

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

  const renderTooltipContent = (props: any) => {
    if (!props.active || !props.payload || props.payload.length === 0)
      return null;

    const { payload } = props;
    const { title, total_duration } = payload[0].payload;

    return (
      <div className="bg-white border border-gray-300 p-2 rounded">
        <p>
          <strong>Name:</strong> {title || "No Name"}
        </p>
        <p>
          <strong>Time:</strong> {secondsToHMSorDays(total_duration)}
        </p>
      </div>
    );
  };

  const handleBarClick = (data: any) => {
    if (data && data.issue_id) {
      navigate(`/issue/${data.issue_id}`);
    }
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
              className="hover:cursor-pointer"
              dataKey="total_duration"
              fill="var(--color-desktop)"
              radius={8}
              onClick={(data) => handleBarClick(data)}
            >
              <LabelList
                position="top"
                offset={12}
                className="fill-foreground"
                fontSize={12}
                formatter={secondsToHMSorDays}
              />
            </Bar>
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
};

export default WorkBarChart;
