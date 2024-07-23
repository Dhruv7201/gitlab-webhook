import { LabelList, RadialBar, RadialBarChart } from "recharts";
import api from "@/utils/api";
import Notification from "@/Notification";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/_ui/card";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/_ui/chart";
import React from "react";

const chartConfig = {
  work_done_count: {
    label: "work_done_count",
  },
} satisfies ChartConfig;

type ChartData = {
  _id: string;
  work_done_count: number;
};

interface Props {
  selectedProjectId: number;
}

const RadialChart: React.FC<Props> = ({ selectedProjectId }) => {
  const [chartData, setChartData] = React.useState<ChartData[]>([]);

  function getColor(data: ChartData[]) {
    const colors = ["#FF6633", "#2563eb", "#FF33FF", "#FFFF99", "#00B3E6"];
    return data
      .sort((a, b) => b.work_done_count - a.work_done_count)
      .map((entry, index) => ({
        ...entry,
        fill: colors[index % colors.length],
      }));
  }

  React.useEffect(() => {


    api
      .post("/work_done", {
        project_id: selectedProjectId,
      })
      .then((response) => {
        const data = response.data;
        if (data.status == false) {
          Notification({ message: data.message, type: "error" });
          return;
        }
        setChartData(getColor(data.data));
      })
      .catch((_error) => {
        Notification({ message: "Problem fetching users", type: "error" });
      });
  }, [selectedProjectId]);
  return (
    <Card>
      <CardHeader className="items-center pb-0">
        <CardTitle>Total task Completed</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 pb-0">
        <ChartContainer
          config={chartConfig}
          className="mx-auto aspect-square max-h-[250px]"
        >
          <RadialBarChart
            data={chartData}
            startAngle={-90}
            endAngle={380}
            innerRadius={30}
            outerRadius={110}
          >
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent hideLabel nameKey="browser" />}
            />
            <RadialBar dataKey="work_done_count" background>
              <LabelList
                position="insideStart"
                dataKey="_id"
                className="fill-white capitalize mix-blend-luminosity"
                fontSize={11}
              />
            </RadialBar>
          </RadialBarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
};
export default RadialChart;
