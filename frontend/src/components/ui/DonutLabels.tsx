"use client";

import * as React from "react";
import { Label, Pie, PieChart } from "recharts";
import "./DonutLabels.css";
import Notification from "@/Notification";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

type CharData = {
  label: string;
  count: number;
  fill: string;
};

const chartConfig = {
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
} as ChartConfig;

interface Props {
  selectedProjectId: number;
}

const DonutLabels: React.FC<Props> = ({ selectedProjectId }) => {
  const [chartData, setChartData] = React.useState<CharData[]>([]);
  const api = import.meta.env.VITE_API_URL;
  const getColor = (data: CharData[]) => {
    const colors = ["#FF6633", "#2563eb", "#FF33FF", "#FFFF99", "#00B3E6"];
    return data.map((entry, index) => ({
      ...entry,
      fill: colors[index % colors.length],
    }));
  };

  React.useEffect(() => {
    if (selectedProjectId === 0) return;
    const fetchData = async () => {
      try {
        const response = await fetch(
          api + `/donut_labels/${selectedProjectId}`
        );
        const data = await response.json();
        if (data.status == false) {
          Notification({ message: data.message, type: "error" });
          return;
        }
        setChartData(getColor(data.data));
      } catch (error) {
        Notification({ message: "Problem fetching users", type: "error" });
      }
    };
    fetchData();
  }, [selectedProjectId]);

  return (
    <>
      <Card className="flex flex-col">
        <CardHeader className="items-center pb-0">
          <CardTitle>Pie Chart - Donut with Text</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 pb-0">
          <ChartContainer
            config={chartConfig}
            className="mx-auto aspect-square max-h-[250px]"
          >
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
                          dominantBaseline="middle"
                        >
                          <tspan
                            x={viewBox.cx}
                            y={viewBox.cy}
                            className="fill-foreground text-3xl font-bold"
                          >
                            {chartData.reduce(
                              (acc: number, { count }: { count: number }) =>
                                acc + count,
                              0
                            )}
                          </tspan>
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
                  }}
                />
              </Pie>
            </PieChart>
          </ChartContainer>
        </CardContent>
      </Card>
    </>
  );
};
export default DonutLabels;
