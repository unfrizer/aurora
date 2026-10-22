import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { blankEditor } from '../src/editor';
import { PhotoTray } from '../src/components/PhotoTray';

const editor = blankEditor('Studio', 'en');
const originalCreate = Object.getOwnPropertyDescriptor(URL, 'createObjectURL');
const originalRevoke = Object.getOwnPropertyDescriptor(URL, 'revokeObjectURL');
let createUrl: ReturnType<typeof vi.fn>;
let revokeUrl: ReturnType<typeof vi.fn>;

function raster(name: string, type = 'image/png', size = 1): File {
  const file = new File(['x'], name, { type });
  Object.defineProperty(file, 'size', { value: size });
  return file;
}

function select(...files: File[]) {
  fireEvent.change(screen.getByLabelText('Choose photos'), { target: { files } });
}

function row(name: string): HTMLElement {
  const found = screen.getByText(name).closest('li');
  if (!found) throw new Error('Missing photo row');
  return found;
}

beforeEach(() => {
  createUrl = vi.fn(() => `blob:photo-${createUrl.mock.calls.length}`);
  revokeUrl = vi.fn();
  Object.defineProperty(URL, 'createObjectURL', { configurable: true, value: createUrl });
  Object.defineProperty(URL, 'revokeObjectURL', { configurable: true, value: revokeUrl });
});

afterEach(() => {
  if (originalCreate) Object.defineProperty(URL, 'createObjectURL', originalCreate);
  else Reflect.deleteProperty(URL, 'createObjectURL');
  if (originalRevoke) Object.defineProperty(URL, 'revokeObjectURL', originalRevoke);
  else Reflect.deleteProperty(URL, 'revokeObjectURL');
});

describe('UI-008 photo tray with UI-011 drop staging', () => {
  it('stages dropped files through picker rules, with no upload from drag or drop', () => {
    const onAttach = vi.fn();
    render(<PhotoTray language="en" editor={editor} onAttach={onAttach} onClose={vi.fn()} />);
    const zone = screen.getByRole('region', { name: 'Photo selection area' });
    expect(screen.getByText(/Dropping does not upload or attach anything/)).toBeInTheDocument();
    fireEvent.dragEnter(zone);
    expect(zone).toHaveClass('dragging');
    expect(screen.queryByRole('button', { name: 'Attach photo' })).not.toBeInTheDocument();
    fireEvent.drop(zone, { dataTransfer: { files: [raster('drop.png')] } });
    expect(zone).not.toHaveClass('dragging');
    expect(screen.getByText('drop.png')).toBeInTheDocument();
    expect(onAttach).not.toHaveBeenCalled();
    expect(screen.getByLabelText('Choose photos')).toBeEnabled();
  });

  it('rejects invalid and over-capacity drops without changing staged photos', () => {
    render(<PhotoTray language="en" editor={editor} onAttach={vi.fn()} onClose={vi.fn()} />);
    const zone = screen.getByRole('region', { name: 'Photo selection area' });
    select(raster('kept.png'));
    fireEvent.drop(zone, { dataTransfer: { files: [raster('valid.jpg', 'image/jpeg'),
      raster('bad.svg', 'image/svg+xml')] } });
    expect(screen.getByText('kept.png')).toBeInTheDocument();
    expect(screen.queryByText('valid.jpg')).not.toBeInTheDocument();
    expect(createUrl).toHaveBeenCalledTimes(1);
    fireEvent.drop(zone, { dataTransfer: { files: Array.from({ length: 20 }, (_, index) =>
      raster(`excess-${index}.png`)) } });
    expect(screen.getAllByRole('button', { name: 'Attach photo' })).toHaveLength(1);
    expect(screen.getByRole('alert')).toHaveTextContent('Your previous selection remains');
  });

  it('stages all four existing raster types without upload and rejects invalid additions atomically', () => {
    const onAttach = vi.fn();
    render(<PhotoTray language="en" editor={editor} onAttach={onAttach} onClose={vi.fn()} />);
    select(raster('one.png'), raster('two.jpg', 'image/jpeg'), raster('three.gif', 'image/gif'),
      raster('four.webp', 'image/webp', 16 * 1024 * 1024));
    expect(screen.getAllByRole('button', { name: 'Attach photo' })).toHaveLength(4);
    expect(createUrl).toHaveBeenCalledTimes(4);
    expect(onAttach).not.toHaveBeenCalled();
    expect(screen.getByText(/does not compress or change them/)).toBeInTheDocument();
    select(raster('bad.svg', 'image/svg+xml'));
    select(raster('empty.png', 'image/png', 0));
    select(raster('too-large.png', 'image/png', 16 * 1024 * 1024 + 1));
    expect(screen.getAllByRole('button', { name: 'Attach photo' })).toHaveLength(4);
    expect(createUrl).toHaveBeenCalledTimes(4);
    expect(screen.getByRole('alert')).toHaveTextContent('Your previous selection remains');
    select(...Array.from({ length: 16 }, (_, index) => raster(`more-${index}.png`)));
    expect(screen.getAllByRole('button', { name: 'Attach photo' })).toHaveLength(20);
    select(raster('overflow.png'));
    expect(screen.getAllByRole('button', { name: 'Attach photo' })).toHaveLength(20);
  });

  it('requires an explicit current target and removes only after confirmed attachment', async () => {
    const onAttach = vi.fn().mockResolvedValue('attached');
    render(<PhotoTray language="en" editor={editor} onAttach={onAttach} onClose={vi.fn()} />);
    const chosen = raster('customer.png');
    select(chosen);
    const item = row('customer.png');
    const button = within(item).getByRole('button', { name: 'Attach photo' });
    expect(button).toBeDisabled();
    const page = editor.pages[0]!;
    const section = page.sections[0]!;
    fireEvent.change(within(item).getByLabelText('Attach to'),
      { target: { value: `${page.id}/${section.id}` } });
    fireEvent.click(button);
    await waitFor(() => expect(onAttach).toHaveBeenCalledExactlyOnceWith(chosen,
      { kind: 'section', pageId: page.id, sectionId: section.id }));
    await waitFor(() => expect(screen.queryByText('customer.png')).not.toBeInTheDocument());
    expect(revokeUrl).toHaveBeenCalledWith('blob:photo-1');
  });

  it('keeps a failed item, prevents parallel attempts and never retries automatically', async () => {
    let finish: ((value: 'save-failed') => void) | undefined;
    const onAttach = vi.fn(() => new Promise<'save-failed'>((resolve) => { finish = resolve; }));
    render(<PhotoTray language="en" editor={editor} onAttach={onAttach} onClose={vi.fn()} />);
    select(raster('waiting.png'), raster('second.png'));
    const item = row('waiting.png');
    fireEvent.change(within(item).getByLabelText('Attach to'), { target: { value: 'logo' } });
    fireEvent.click(within(item).getByRole('button', { name: 'Attach photo' }));
    expect(screen.getByRole('button', { name: 'Attaching…' })).toBeDisabled();
    expect(within(row('second.png')).getByRole('button', { name: 'Attach photo' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Close' })).toBeDisabled();
    expect(screen.getByLabelText('Choose photos')).toBeDisabled();
    const zone = screen.getByRole('region', { name: 'Photo selection area' });
    fireEvent.drop(zone, { dataTransfer: { files: [raster('blocked.png')] } });
    expect(screen.queryByText('blocked.png')).not.toBeInTheDocument();
    expect(onAttach).toHaveBeenCalledTimes(1);
    finish?.('save-failed');
    expect(await screen.findByRole('alert')).toHaveTextContent('file may be stored');
    expect(screen.getByText('waiting.png')).toBeInTheDocument();
    expect(onAttach).toHaveBeenCalledTimes(1);
  });

  it('disables a removed stable target and revokes all remaining previews on close', () => {
    const onAttach = vi.fn();
    const onClose = vi.fn();
    const { rerender, unmount } = render(<PhotoTray language="en" editor={editor} onAttach={onAttach} onClose={onClose} />);
    select(raster('first.png'), raster('second.png'));
    const first = row('first.png');
    const page = editor.pages[0]!;
    const section = page.sections[0]!;
    fireEvent.change(within(first).getByLabelText('Attach to'),
      { target: { value: `${page.id}/${section.id}` } });
    rerender(<PhotoTray language="en" editor={{ ...editor, pages: [{ ...page, sections: [] }] }}
      onAttach={onAttach} onClose={onClose} />);
    expect(within(row('first.png')).getByRole('button', { name: 'Attach photo' })).toBeDisabled();
    fireEvent.click(within(row('second.png')).getByRole('button', { name: 'Delete' }));
    expect(revokeUrl).toHaveBeenCalledWith('blob:photo-2');
    fireEvent.click(screen.getByRole('button', { name: 'Close' }));
    expect(onClose).toHaveBeenCalledTimes(1);
    unmount();
    expect(revokeUrl).toHaveBeenCalledWith('blob:photo-1');
  });

  it('shows localized Russian guidance and requires a manual destination', () => {
    render(<PhotoTray language="ru" editor={editor} onAttach={vi.fn()} onClose={vi.fn()} />);
    expect(screen.getByText(/Файлы загружаются только при прикреплении/)).toBeInTheDocument();
    expect(screen.getByRole('region', { name: 'Область выбора фотографий' })).toHaveTextContent('Перетаскивание ничего не загружает');
    fireEvent.change(screen.getByLabelText('Выбрать фотографии'),
      { target: { files: [raster('ru.png')] } });
    expect(within(row('ru.png')).getByRole('button', { name: 'Прикрепить фотографию' })).toBeDisabled();
  });
});
