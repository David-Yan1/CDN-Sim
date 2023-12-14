import React, { useEffect, useRef } from "react";

const ResultsMap = ({ data }) => {
  const canvasRef = useRef(null);
  const WIDTH = 600;
  const HEIGHT = 300;

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const background = new Image();
    background.src =
      "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Blue_Marble_2002.png/390px-Blue_Marble_2002.png";

    background.onload = () => {
      ctx.drawImage(background, 0, 0, canvas.width, canvas.height);
      drawMapElements();
    };

    const drawMapElements = () => {
      data.user_locations.forEach((loc) => {
        drawDot(loc, "red");
      });
      drawDot(data.origin_location, "blue");
      data.node_locations.forEach((loc) => {
        drawDot(loc, "green");
      });
      data.requests.forEach((req) => drawLine(req[0], req[1], "red"));
    };

    const drawDot = (location, color) => {
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(
        scale(location[0], WIDTH),
        scale(location[1], HEIGHT),
        5,
        0,
        2 * Math.PI
      );
      ctx.fill();
    };

    const drawLine = (start, end, color) => {
      ctx.strokeStyle = color;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(scale(start[0], WIDTH), scale(start[1], HEIGHT));
      ctx.lineTo(scale(end[0], WIDTH), scale(end[1], HEIGHT));
      ctx.stroke();
    };

    const scale = (coordinate, dimension) => {
      return coordinate * (dimension / 100);
    };
  }, [data]);

  return (
    <>
      <canvas ref={canvasRef} width={WIDTH} height={HEIGHT}></canvas>
      <p style={{ fontSize: "20px" }}>
        🔴 = 100 users 🟢 = Edge server 🔵 = Origin server
      </p>
    </>
  );
};

export default ResultsMap;
