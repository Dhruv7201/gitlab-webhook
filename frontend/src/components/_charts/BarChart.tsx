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
  ChartContainer
} from "@/components/_ui/chart";
import { secondsToHMSorDays } from "@/utils/timeFormate";
import { useNavigate } from "react-router-dom";

const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "hsl(var(--chart-1))",
    format: "time_formats",
  },
} as ChartConfig;

type BarData = {
  name: string;
  user_id: number;
  time_waste: number;
};

interface Props {
  selectedProjectId: number;
  dateRange: any;
}

const Barchart: React.FC<Props> = ({ selectedProjectId, dateRange }) => {
  const [barData, setBarData] = React.useState<BarData[]>([]);
  const navigate = useNavigate();

  const handleBarClick = (data: any) => {
    if (data?.user_id) {
      navigate(`/user/${data.user_id}`);
    }
  };

  React.useEffect(() => {
    api
      .post(`/user_time_waste`, {
        project_id: selectedProjectId,
        dateRange,
      })
      .then((response) => {
        const data = response.data;
        if (data.status === false) {
          Notification({ message: data.message, type: "error" });
          return;
        }
        setBarData(data.data);
      })
      .catch((error) => {
        console.error(error);

        if (
          error?.response &&
          error?.response?.data &&
          error?.response?.data?.detail
        ) {
          const detail = error.response.data.detail;
          Notification({ message: detail.message, type: "error" });
        } else {
          Notification({ message: error.message, type: "error" });
        }
      });
  }, [selectedProjectId, dateRange]);

  const renderTooltipContent = (props: any) => {
    if (!props.active || !props.payload || props.payload.length === 0)
      return null;

    const { payload } = props;
    const { name, time_waste } = payload[0].payload;

    return (
      <div className="bg-white border border-gray-300 p-2 rounded">
        <p>
          <strong>Name:</strong> {name || "No Name"}
        </p>
        <p>
          <strong>Time:</strong> {secondsToHMSorDays(time_waste)}
        </p>
      </div>
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>User Idle Time</CardTitle>
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
              dataKey="name"
              tickLine={false}
              tickMargin={10}
              axisLine={false}
              tickFormatter={(value) => value.slice(0, 3)}
            />
            <Tooltip content={renderTooltipContent} />
            <Bar
              dataKey="time_waste"
              fill="var(--color-desktop)"
              radius={8}
              onClick={(data) => handleBarClick(data)}
              className="hover:cursor-pointer"
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

export default Barchart;
