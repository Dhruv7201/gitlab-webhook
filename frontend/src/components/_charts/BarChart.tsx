import * as React from "react";
import api from "@/utils/api";
import { Bar, BarChart, CartesianGrid, LabelList, XAxis } from "recharts";
import Notification from "../../Notification";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/_ui/card";
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
};

interface Props {
  selectedProjectId: number;
}

const Barchart: React.FC<Props> = ({ selectedProjectId }) => {
  const [barData, setBarData] = React.useState<BarData[]>([]);

  const project_id = localStorage.getItem("selectedProjectId");

  React.useEffect(() => {

  
    api
      .post(`/user_time_waste`, {
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
      .catch((error) => {
        console.error(error);
  
        // Check if the error response has a detail field
        if (error.response && error.response.data && error.response.data.detail) {
          const detail = error.response.data.detail;
          Notification({ message: detail.message, type: "error" });
        } else {
          Notification({ message: error.message, type: "error" });
        }
      });
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
        {project_id ? (
          <CardTitle>User Idle Time</CardTitle>
        ) : (
          <CardTitle>Select Project</CardTitle>
        )}
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
              dataKey="name"
              tickLine={false}
              tickMargin={10}
              axisLine={false}
              tickFormatter={(value) => value.slice(0, 3)}
            />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent hideLabel />}
              formatter={renderLabel1}
            />
            <Bar dataKey="time_waste" fill="var(--color-desktop)" radius={8}>
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

export default Barchart;
