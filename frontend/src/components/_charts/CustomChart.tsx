import * as React from "react";
import api from "@/utils/api";
import { useNavigate } from "react-router-dom";
import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  XAxis,
  YAxis,
} from "recharts";
import Notification from "@/Notification";
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
  },
  mobile: {
    label: "Mobile",
    color: "hsl(var(--chart-2))",
  },
  label: {
    color: "hsl(var(--background))",
  },
} satisfies ChartConfig;

interface Props {
  selectedProjectId: number;
  dateRange: any;
}

type ChartData = {
  _id: string;
  work_done_count: number;
  user_id: number;
};

const CustomChart: React.FC<Props> = ({ selectedProjectId, dateRange }) => {
  const [chartData, setChartData] = React.useState<ChartData[]>([]);
  const navigate = useNavigate();

  const handleBarClick = (data: any) => {
    if (data && data.user_id) {
      navigate(`/user/${data.user_id}`);
    }
  };

  React.useEffect(() => {
    api
      .post(`/work_done`, {
        project_id: selectedProjectId,
        dateRange,
      })
      .then((response) => {
        const data = response.data;
        if (data.status == false) {
          Notification({ message: data.message, type: "error" });
          return;
        }
        setChartData(data.data);
      })
      .catch((_error) => {
        Notification({ message: "Problem fetching users", type: "error" });
      });
  }, [selectedProjectId, dateRange]);
  return (
    <Card>
      <CardHeader>
        <CardTitle>work done by user</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <BarChart
            accessibilityLayer
            data={chartData}
            layout="vertical"
            margin={{
              right: 16,
            }}
          >
            <CartesianGrid horizontal={false} />
            <YAxis
              dataKey="_id"
              type="category"
              tickLine={false}
              tickMargin={10}
              axisLine={false}
              tickFormatter={(value) => value.slice(0, 3)}
              hide
            />
            <XAxis dataKey="work_done_count" type="number" hide />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent indicator="line" />}
            />
            <Bar
              className="hover:cursor-pointer"
              dataKey="work_done_count"
              layout="vertical"
              fill="var(--color-desktop)"
              onClick={(data) => handleBarClick(data)}
              radius={4}
            >
              <LabelList
                dataKey="_id"
                position="insideLeft"
                offset={8}
                className="fill-[--color-label]"
                fontSize={12}
              />
              <LabelList
                dataKey="work_done_count"
                position="right"
                offset={8}
                className="fill-foreground"
                fontSize={12}
              />
            </Bar>
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
};
export default CustomChart;
