param(
    [Parameter(Mandatory = $true)]
    [string[]]$InputPath,
    [hashtable]$InteriorSeeds = @{}
)

Add-Type -AssemblyName System.Drawing

$source = @'
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;

public static class CheckerboardAlphaCleaner
{
    private const int BackgroundFloor = 225;
    private const int MaxBackgroundChroma = 8;

    public static void Clean(string inputPath, string outputPath)
    {
        Clean(inputPath, outputPath, new int[0]);
    }

    public static void Clean(string inputPath, string outputPath, int[] interiorSeeds)
    {
        using (var source = new Bitmap(inputPath))
        using (var output = new Bitmap(source.Width, source.Height, PixelFormat.Format32bppArgb))
        {
            using (var graphics = Graphics.FromImage(output))
            {
                graphics.DrawImageUnscaled(source, 0, 0);
            }

            var rect = new Rectangle(0, 0, output.Width, output.Height);
            var data = output.LockBits(rect, ImageLockMode.ReadWrite, PixelFormat.Format32bppArgb);
            var bytes = Math.Abs(data.Stride) * output.Height;
            var pixels = new byte[bytes];
            Marshal.Copy(data.Scan0, pixels, 0, bytes);

            var visited = new bool[output.Width * output.Height];
            var queue = new Queue<int>();

            for (var x = 0; x < output.Width; x++)
            {
                EnqueueIfBackground(x, 0, output.Width, output.Height, data.Stride, pixels, visited, queue);
                EnqueueIfBackground(x, output.Height - 1, output.Width, output.Height, data.Stride, pixels, visited, queue);
            }

            for (var y = 0; y < output.Height; y++)
            {
                EnqueueIfBackground(0, y, output.Width, output.Height, data.Stride, pixels, visited, queue);
                EnqueueIfBackground(output.Width - 1, y, output.Width, output.Height, data.Stride, pixels, visited, queue);
            }

            for (var i = 0; i + 1 < interiorSeeds.Length; i += 2)
            {
                EnqueueIfBackground(interiorSeeds[i], interiorSeeds[i + 1], output.Width, output.Height, data.Stride, pixels, visited, queue);
            }

            while (queue.Count > 0)
            {
                var index = queue.Dequeue();
                var x = index % output.Width;
                var y = index / output.Width;
                var offset = y * data.Stride + x * 4;
                pixels[offset + 3] = 0;

                EnqueueIfBackground(x - 1, y, output.Width, output.Height, data.Stride, pixels, visited, queue);
                EnqueueIfBackground(x + 1, y, output.Width, output.Height, data.Stride, pixels, visited, queue);
                EnqueueIfBackground(x, y - 1, output.Width, output.Height, data.Stride, pixels, visited, queue);
                EnqueueIfBackground(x, y + 1, output.Width, output.Height, data.Stride, pixels, visited, queue);
            }

            Marshal.Copy(pixels, 0, data.Scan0, bytes);
            output.UnlockBits(data);
            output.Save(outputPath, ImageFormat.Png);
        }
    }

    private static void EnqueueIfBackground(
        int x,
        int y,
        int width,
        int height,
        int stride,
        byte[] pixels,
        bool[] visited,
        Queue<int> queue)
    {
        if (x < 0 || y < 0 || x >= width || y >= height)
        {
            return;
        }

        var index = y * width + x;
        if (visited[index])
        {
            return;
        }

        visited[index] = true;
        var offset = y * stride + x * 4;
        var blue = pixels[offset];
        var green = pixels[offset + 1];
        var red = pixels[offset + 2];
        var max = Math.Max(red, Math.Max(green, blue));
        var min = Math.Min(red, Math.Min(green, blue));

        if (min >= BackgroundFloor && max - min <= MaxBackgroundChroma)
        {
            queue.Enqueue(index);
        }
    }
}
'@

Add-Type -TypeDefinition $source -ReferencedAssemblies System.Drawing

foreach ($path in $InputPath) {
    $resolved = (Resolve-Path -LiteralPath $path).Path
    $temporary = "$resolved.alpha.png"
    $seeds = if ($InteriorSeeds.ContainsKey([System.IO.Path]::GetFileName($resolved))) {
        [int[]]$InteriorSeeds[[System.IO.Path]::GetFileName($resolved)]
    } else {
        [int[]]@()
    }
    [CheckerboardAlphaCleaner]::Clean($resolved, $temporary, $seeds)
    Move-Item -LiteralPath $temporary -Destination $resolved -Force
}
