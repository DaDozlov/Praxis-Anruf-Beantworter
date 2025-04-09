import React, { useMemo, useState, useEffect } from 'react';
import Card from './Card';
import {
  ColumnDef,
  flexRender,
  getSortedRowModel,
  getFilteredRowModel,
  getCoreRowModel,
  getPaginationRowModel,
  getExpandedRowModel,
  useReactTable,
  RowSelectionState,
  SortingState,
  ExpandedState,
  ColumnFiltersState,
} from '@tanstack/react-table';
import { Message } from '../types';
import {
  Phone,
  User,
  ArrowDownUp,
  Triangle,
  ArrowUp,
  ArrowDown,
  Trash,
  Search,
  Weight,
} from 'lucide-react';
import { SlArrowRight, SlArrowDown } from 'react-icons/sl';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Rating } from 'react-simple-star-rating';
import { useGetLatest } from 'react-table';

const BasicTable: React.FC = () => {
  /**
   * When the component mounts, we fetch initial data:
   *  - all emails from our backend
   *  - current Whisper model
   *  - last scheduler run time
   * Then we apply a default filter for 'unbearbeitet' (unprocessed) records.
   */
  useEffect(() => {
    const fetchData = async () => {
      try {
        const emailResponse = await fetch('http://127.0.0.1:5000/all');
        const emails = await emailResponse.json();
        setData(emails);

        const modelResponse = await fetch(
          'http://127.0.0.1:5000/get-whisper-model',
        );
        const modelData = await modelResponse.json();
        if (modelData.model) {
          setWhisperModel(modelData.model);
        }

        await fetchSchedulerTime();
      } catch (error) {
        console.error('Error initializing data:', error);
      }
    };

    fetchData();
    filterStatus('unbearbeitet');

  }, []);

  const [lastSchedulerUpdate, setLastSchedulerUpdate] = useState<string | null>(
    null,
  );

  /**
   * Fetch the last scheduler run time from the backend
   * and update state with formatted string or error info.
   */
  const fetchSchedulerTime = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/last-scheduler-run');
      const data = await response.json();
      if (data.last_run) {
        setLastSchedulerUpdate(new Date(data.last_run).toLocaleString());
      } else {
        setLastSchedulerUpdate('Noch keine Updates');
      }
    } catch (error) {
      console.error('Fehler beim Abrufen der Scheduler-Zeit:', error);
      setLastSchedulerUpdate('Fehler beim Abrufen der Zeit');
    }
  };

  /**
   * Reload the data from the server and force a refresh
   */
  const handleReload = async () => {
    try {
      const emailResponse = await fetch('http://127.0.0.1:5000/all');
      const emails = await emailResponse.json();
      setData(emails);

      await fetchSchedulerTime();

      window.location.reload();
    } catch (error) {
      console.error('Fehler beim Neuladen der Daten:', error);
    }
  };

  const [whisperModel, setWhisperModel] = useState<string>('tiny');
  /**
   * Send a selected Whisper model name to the server to update
   */
  const setWhisperModelOnServer = async (model: string) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:5000/set-whisper-model?model=${model}`,
        { method: 'POST' },
      );

      if (!response.ok) throw new Error('Failed to update Whisper model');

      const data = await response.json();
      alert(data.message || `Whisper model set to ${model}`);
      setWhisperModel(model); // Update frontend state
    } catch (error) {
      console.error('Error updating Whisper model:', error);
      alert('Failed to update Whisper model');
    }
  };

  /**
   * Format a date string from the server into a more human-readable
   * 'Heute um HH:MM' or 'Gestern um HH:MM' format, or a typical date-time for older dates
   */
  const formatDate = (date: string) => {
    const fDate = new Date(date);

    const today = new Date();
    const yesterday = new Date();
    yesterday.setDate(today.getDate() - 1);

    const optionsDate: Intl.DateTimeFormatOptions = {
      weekday: 'short',
      month: 'numeric',
      day: 'numeric',
    };

    const optionsTime: Intl.DateTimeFormatOptions = {
      hour: '2-digit',
      minute: '2-digit',
      second: undefined,
    };

    if (today.toDateString() === fDate.toDateString())
      return `Heute um ${fDate.toLocaleTimeString('de-DE', optionsTime)}`;
    if (yesterday.toDateString() === fDate.toDateString())
      return `Gestern um ${fDate.toLocaleTimeString('de-DE', optionsTime)}`;

    return `${fDate.toLocaleDateString('de-DE', optionsDate)} um ${fDate.toLocaleTimeString('de-DE', optionsTime)}`;
  };

  /**
   * Change the 'status' of a message in local state AND in the database
   */
  const changeStatus = (status: string, id: string) => {
    const updatedData: Message[] = data.map((message) => {
      if (message.id === id) return { ...message, status: status };
      return message;
    });

    setData(updatedData);

    fetch(
      `http://127.0.0.1:5000/update?id=${id}&column=status&value=${status}`,
      {
        method: 'POST',
      },
    )
      .then((resp) => resp.json())
      .then((resp) => console.log(resp))
      .catch((error) => console.log(error));
  };

  const [activeTab, setActiveTab] = useState<string>('unbearbeitet');

  const [sorting, setSorting] = useState<SortingState>([
    {
      id: 'empfangsdatum',
      desc: true,
    },
  ]);

  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 10,
  });

  const [rowSelection, setRowSelection] = useState<RowSelectionState>({});

  const [globalFilter, setGlobalFilter] = useState<string>('');

  const [expanded, setExpanded] = useState<ExpandedState>({});

  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);

  const [loading, setLoading] = useState(false);


  /**
   * Reprocess an audio file on the server by ID, then refresh the table
   */
  const reprocessAudio = (emailId: string) => {
    setLoading(true);
    fetch(`http://127.0.0.1:5000/reprocess?id=${emailId}`, {
      method: 'POST',
    })
      .then((response) => {
        setLoading(false);
        if (!response.ok) {
          throw new Error('Audio konnte nicht erneut verarbeitet werden');
        }
        return response.json();
      })
      .then(() => {
        window.location.reload();
      })
      .catch((error) => {
        setLoading(false);
        console.error(error);
      });
  };

  /**
   * Define the columns for react-table, referencing fields in our Message interface
   */
  const columns = useMemo<ColumnDef<Message>[]>(
    () => [
      {
        header: ' ',
        cell: ({ row }) => {
          return row.getCanExpand() ? (
            <span>
              {row.getIsExpanded() ? <SlArrowDown /> : <SlArrowRight />}
            </span>
          ) : (
            ''
          );
        },
        enableSorting: false,
      },

      {
        accessorKey: 'nachname',
        header: () => <span style={{ cursor: 'pointer' }}>Nachname </span>,
      },

      {
        accessorKey: 'vorname',
        header: () => <span style={{ cursor: 'pointer' }}>Vorname </span>,
      },

      {
        accessorKey: 'telefonnummer',
        header: () => <span style={{ cursor: 'pointer' }}>Telefon </span>,
      },

      {
        accessorKey: 'status',
        header: () => <span style={{ cursor: 'pointer' }}>Status </span>,
        cell: ({ row }) => {
          const status = row.original.status;
          switch (status) {
            case 'unbearbeitet':
              return <td>Unbearbeitet</td>;
            case 'bearbeitet':
              return <td>Bearbeitet</td>;
            case 'abfertigung':
              return <td>In Bearbeitung</td>;
            case 'fehlgeschlagen':
              return <td>Fehlgeschlagen</td>;
            default:
              return <td>{status}</td>;
          }
        },
        filterFn: (row, columnId, filterValue) => {
          return row.getValue(columnId) === filterValue;
        },
      },

      {
        accessorKey: 'empfangsdatum',
        header: () => <span style={{ cursor: 'pointer' }}>Eingang </span>,
        cell: ({ row }) => <td>{formatDate(row.original.empfangsdatum)}</td>,
      },

      {
        accessorKey: 'anfragetyp',
        header: () => <span style={{ cursor: 'pointer' }}>Typ </span>,
      },

      {
        id: 'select-col',
        header: ({ table }) => (
          <input
            type="checkbox"
            checked={
              table.getIsAllRowsSelected() && activeTab !== 'unbearbeitet'
            }
            onChange={table.getToggleAllRowsSelectedHandler()}
          />
        ),
        cell: ({ row }) => (
          <input
            type="checkbox"
            checked={row.getIsSelected()}
            disabled={!row.getCanSelect()}
            onClick={(e) => {
              row.getToggleSelectedHandler()(e);
              e.stopPropagation();
            }}
          />
        ),
        enableSorting: false,
      },
    ],
    [],
  );
  const [data, setData] = useState<Message[]>([]);

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onPaginationChange: setPagination,
    getFilteredRowModel: getFilteredRowModel(),
    onRowSelectionChange: setRowSelection,
    enableRowSelection: (row) => row.original.status == 'bearbeitet',
    getSortedRowModel: getSortedRowModel(),
    getExpandedRowModel: getExpandedRowModel(),
    getRowCanExpand: (row) => row.original.status !== 'abfertigung',
    onExpandedChange: setExpanded,
    onGlobalFilterChange: setGlobalFilter,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    state: {
      sorting,
      globalFilter,
      pagination,
      rowSelection,
      expanded,
      columnFilters,
    },
  });


  /**
   * Delete all currently selected rows from both the UI state and the server
   */
  const deleteSelectedRows = () => {
    const selectedRowsIds = table
      .getSelectedRowModel()
      .rows.map((row) => row.original.id);
    const newData = data.filter(
      (message) => !selectedRowsIds.includes(message.id),
    );
    setData(newData);
    table.resetRowSelection();

    selectedRowsIds.forEach((id) => {
      fetch(`http://127.0.0.1:5000/delete?id=${id}`, {
        method: 'POST',
      })
        .then((resp) => resp.json)
        .then((resp) => console.log(resp))
        .catch((error) => console.log(error));
    });
  };

  /**
   * Change the rating of a specific row, updating local state and then the server
   */
  const changeRating = (newRating: number, id: string) => {
    const updatedData: Message[] = data.map((message) => {
      if (message.id === id) {
        return { ...message, rating: newRating };
      }
      return message;
    });

    setData(updatedData);

    fetch(
      `http://127.0.0.1:5000/update?id=${id}&column=rating&value=${newRating}`,
      {
        method: 'POST',
      },
    )
      .then((resp) => resp.json())
      .then((resp) => console.log(resp))
      .catch((error) => console.log(error));
  };

  /**
   * Filter data in the table by 'status'
   */
  const filterStatus = (status: string) => {
    table.getColumn('status')?.setFilterValue(status);
    setActiveTab(status);
    table.resetExpanded();
  };

  return (

    <div className="container mt-5 p-0">
      {/* Header bar: title, last-scheduler-update, Whisper model selector */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Praxis-Anrufbeantworter-Transkription</h2>
        <div className="d-flex align-items-center">
          <button
            className="btn btn-secondary me-3"
            onClick={handleReload}
            disabled={!data.length}
          >
            Aktualisieren
          </button>
          <span className="text-muted">
            Letzter Nachrichtenabruf: {lastSchedulerUpdate || 'Loading...'}
          </span>
        </div>
        <div>
          <label className="me-2">Whisper Modell:</label>
          <select
            value={whisperModel}
            onChange={(e) => {
              const selectedModel = e.target.value;
              setWhisperModel(selectedModel); // Update frontend state
              setWhisperModelOnServer(selectedModel); // Notify backend
            }}
            className="form-select d-inline-block"
            style={{ width: '150px' }}
          >
            <option value="tiny">tiny</option>
            <option value="base">base</option>
            <option value="small">small</option>
            <option value="medium">medium</option>
            <option value="large">large</option>
          </select>
        </div>
      </div>

      {/* Navigation Tabs: 'unbearbeitet', 'alle', 'bearbeitet' */}
      <ul className="nav nav-tabs" role="tablist">
        <li className="nav-item">
          <button
            className={`nav-link ${activeTab === 'unbearbeitet' ? 'active' : ''}`}
            style={{ color: 'black' }}
            onClick={() => filterStatus('unbearbeitet')}
          >
            Unbearbeitet (
            {data.filter((d) => d.status === 'unbearbeitet').length})
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${activeTab === '' ? 'active' : ''}`}
            style={{ color: 'black' }}
            onClick={() => filterStatus('')}
          >
            Alle ({data.length})
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${activeTab === 'bearbeitet' ? 'active' : ''}`}
            style={{ color: 'black' }}
            onClick={() => filterStatus('bearbeitet')}
          >
            Bearbeitet ({data.filter((d) => d.status === 'bearbeitet').length})
          </button>
        </li>
      </ul>
      {/* Main container for table / search / page size selection / delete icon */}
      <div className="container p-5 my-5 border rounded mt-0">
        <div className="input-group">
          <div className="input-group-prepend">
            <div className="input-group-text">
              <Search />
            </div>
          </div>
          <input
            className="form-control"
            value={globalFilter}
            onChange={(e) =>
              table.setGlobalFilter(String(e.currentTarget.value))
            }
            placeholder="Suche..."
          />
        </div>
        {/* Expanded row content (shows Card details) */}
        <table className="table table-hover p-5 my-5 border rounded">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th key={header.id} colSpan={header.colSpan}>
                    {header.isPlaceholder ? null : (
                      <div
                        className={
                          header.column.getCanSort()
                            ? 'cursor-pointer select-none'
                            : ''
                        }
                        onClick={header.column.getToggleSortingHandler()}
                        title={
                          header.column.getCanSort()
                            ? header.column.getNextSortingOrder() === 'asc'
                              ? 'Sort ascending'
                              : header.column.getNextSortingOrder() === 'desc'
                                ? 'Sort descending'
                                : 'Clear sort'
                            : undefined
                        }
                      >
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext(),
                        )}
                        {{
                          asc: <ArrowUp size={17} />,
                          desc: <ArrowDown size={17} />,
                        }[header.column.getIsSorted() as string] ??
                          (header.column.getCanSort() ? (
                            <ArrowDownUp size={17} />
                          ) : null)}
                      </div>
                    )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => (
              <React.Fragment key={row.id}>
                {/* Normal row UI */}
                <tr
                  className={
                    row.original.status === 'bearbeitet' ? 'table-light' : ''
                  }
                  onClick={row.getToggleExpandedHandler()}
                  style={{ cursor: 'pointer' }}
                >
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </td>
                  ))}
                </tr>
                {/* If the row is expanded, render the expanded UI as a separate row with a single cell that spans the width of the table */}
                {row.getIsExpanded() && (
                <tr>
                  <td colSpan={row.getAllCells().length}>
                    {row.original.anfragetyp === 'Rezept' ? (
                      <Card
                        id={row.original.id}
                        type={row.original.anfragetyp}
                        state={row.original.status}
                        rating={row.original.rating}
                        lines={{
                          Nachname: row.original.nachname === 'None' ? '' : row.original.nachname,
                          Vorname: row.original.vorname === 'None' ? '' : row.original.vorname,
                          Geburtsdatum: row.original.geburtsdatum === 'None' ? '' : row.original.geburtsdatum,
                          Medikament: row.original.nameMedikament === 'None' ? '' : row.original.nameMedikament,
                          Menge: row.original.dosis === 'None' ? '' : row.original.dosis,
                          Extra: row.original.extraInformation === 'None' ? '' : row.original.extraInformation,
                          Nachricht: row.original.transkript === 'None' ? '' : row.original.transkript,
                        }}
                        changeStatus={changeStatus}
                        changeRating={changeRating}
                        reprocessAudio={reprocessAudio}
                      />
                    ) : row.original.anfragetyp === 'Überweisung' ? (
                      <Card
                        id={row.original.id}
                        type={row.original.anfragetyp}
                        state={row.original.status}
                        rating={row.original.rating}
                        lines={{
                          Nachname: row.original.nachname === 'None' ? '' : row.original.nachname,
                          Vorname: row.original.vorname === 'None' ? '' : row.original.vorname,
                          Geburtsdatum: row.original.geburtsdatum === 'None' ? '' : row.original.geburtsdatum,
                          Fachrichtung: row.original.fachrichtung === 'None' ? '' : row.original.fachrichtung,
                          'Grund für Überweisung': row.original.grundUeberweisung === 'None' ? '' : row.original.grundUeberweisung,
                          Extra: row.original.extraInformation === 'None' ? '' : row.original.extraInformation,
                          Nachricht: row.original.transkript === 'None' ? '' : row.original.transkript,
                        }}
                        changeStatus={changeStatus}
                        changeRating={changeRating}
                        reprocessAudio={reprocessAudio}
                      />
                    ) : (
                      // Fallback for any other anfragetyp
                      <Card
                        id={row.original.id}
                        type={row.original.anfragetyp}
                        state={row.original.status}
                        rating={row.original.rating}
                        lines={{
                          Nachname: row.original.nachname === 'None' ? '' : row.original.nachname,
                          Vorname: row.original.vorname === 'None' ? '' : row.original.vorname,
                          Geburtsdatum: row.original.geburtsdatum === 'None' ? '' : row.original.geburtsdatum,
                          Medikament: row.original.nameMedikament === 'None' ? '' : row.original.nameMedikament,
                          Menge: row.original.dosis === 'None' ? '' : row.original.dosis,
                          Extra: row.original.extraInformation === 'None' ? '' : row.original.extraInformation,
                          Nachricht: row.original.transkript === 'None' ? '' : row.original.transkript,
                        }}
                        changeStatus={changeStatus}
                        changeRating={changeRating}
                        reprocessAudio={reprocessAudio}
                      />
                    )}
                  </td>
                </tr>
              )}
              </React.Fragment>
            ))}
          </tbody>
        </table>

        {/* Page size selection & Delete button for selected rows */}
        <div className="d-flex d-flex d-flex justify-content-between">
          <div>
            <select
              className="form-select"
              id="pageSelect"
              value={table.getState().pagination.pageSize}
              onChange={(e) => {
                table.setPageSize(Number(e.target.value));
              }}
            >
              {' '}
              {[10, 20, 30, 40, 50].map((pageSize) => (
                <option key={pageSize} value={pageSize}>
                  {' '}
                  {pageSize}{' '}
                </option>
              ))}{' '}
            </select>
          </div>
          <div className="mr-2">
            <Trash
              style={{ cursor: 'pointer' }}
              size={25}
              onClick={() => deleteSelectedRows()}
            />{' '}
          </div>
        </div>
      </div>

      {/* Pagination controls: First page, Previous, Next, Last */}
      <div className="d-flex flex-column align-items-center">
        {' '}
        <div>
          <ul className="pagination">
            <li
              className={`page-item ${!table.getCanPreviousPage() ? 'disabled' : ''}`}
            >
              <button
                type="button"
                className="page-link"
                onClick={() => table.firstPage()}
                disabled={!table.getCanPreviousPage()}
              >
                {' '}
                &laquo;{' '}
              </button>{' '}
            </li>
            <li
              className={`page-item ${!table.getCanPreviousPage() ? 'disabled' : ''}`}
            >
              <button
                type="button"
                className="page-link"
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
              >
                {' '}
                &lt;{' '}
              </button>{' '}
            </li>
            <li
              className={`page-item ${!table.getCanNextPage() ? 'disabled' : ''}`}
            >
              <button
                type="button"
                className="page-link"
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
              >
                {' '}
                &gt;{' '}
              </button>{' '}
            </li>
            <li
              className={`page-item ${!table.getCanNextPage() ? 'disabled' : ''}`}
            >
              <button
                type="button"
                className="page-link"
                onClick={() => table.lastPage()}
                disabled={!table.getCanNextPage()}
              >
                {' '}
                &raquo;{' '}
              </button>{' '}
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default BasicTable;
