import api from "@/utils/api";
import * as React from "react";
import { Label, Pie, PieChart } from "recharts";
import Notification from "@/Notification";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/_ui/card";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
} from "@/components/_ui/chart";
import { DateRange } from "react-day-picker";

type ChartData = {
  label: string;
  count: number;
  fill: string;
};

const chartConfig: ChartConfig = {
  total: {
    label: "Total",
  },
  Doing: {
    label: "Doing",
    color: "hsl(var(--chart-0))",
  },
  Doc: {
    label: "Doc",
    color: "hsl(var(--chart-2))",
  },
  testing: {
    label: "Testing",
    color: "hsl(var(--chart-3))",
  },
};

interface Props {
  selectedProjectId: number;
  dateRange?: DateRange;
}

const DonutLabels: React.FC<Props> = ({ selectedProjectId, dateRange }) => {
  const [chartData, setChartData] = React.useState<ChartData[]>([]);

  const getColor = (data: ChartData[]) => {
    const colors = ["#FF6633", "#2563eb", "#FF33FF", "#FFFF99", "#00B3E6"];
    return data.map((entry, index) => ({
      ...entry,
      fill: colors[index % colors.length],
    }));
  };

  React.useEffect(() => {


    api
      .post(`/donut_labels/`, {
        project_id: selectedProjectId,
        date_range: dateRange,
      })
      .then((response) => {
        const data = response.data;
        if (!data.status) {
          Notification({ message: data.message, type: "error" });
          return;
        }

        setChartData(getColor(data.data));
      })
      .catch((_error) => {
        Notification({ message: "Problem fetching data", type: "error" });
      });
  }, [selectedProjectId, dateRange]);

  return (
    <Card className="flex flex-col">
      <CardHeader>
        <CardTitle>Labels</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <PieChart>
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent hideLabel />}
            />
            <Pie
              data={chartData}
              dataKey="count"
              nameKey="label"
              innerRadius={60}
              strokeWidth={5}
            >
              <Label
                content={({ viewBox }) => {
                  if (viewBox && "cx" in viewBox && "cy" in viewBox) {
                    return (
                      <text
                        x={viewBox.cx}
                        y={viewBox.cy}
                        textAnchor="middle"
                        className="fill-foreground text-3xl font-bold"
                      >
                        {chartData.reduce(
                          (acc: number, { count }: { count: number }) =>
                            acc + count,
                          0
                        )}
                        <tspan
                          x={viewBox.cx}
                          y={(viewBox.cy || 0) + 24}
                          className="fill-muted-foreground"
                        >
                          Total
                        </tspan>
                      </text>
                    );
                  }
                  return null;
                }}
              />
            </Pie>
            {chartData.map((entry, _index) => (
              <ChartLegend key={entry.label} color={entry.fill} />
            ))}
          </PieChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
};

export default DonutLabels;
